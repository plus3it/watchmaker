#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$PYTHON = "3.12"

# Extract versions from project files
$VERSION = (Select-String -Path "pyproject.toml" -Pattern '^version\s*=\s*"([^"]+)"').Matches.Groups[1].Value
$PYAPP_VERSION = (Select-String -Path ".github/workflows/dependabot_hack.yml" -Pattern 'ofek/pyapp@v([0-9.]+)').Matches.Groups[1].Value
$PYTHON_BUILD_STANDALONE_VERSION = (Select-String -Path ".github/workflows/dependabot_hack.yml" -Pattern 'python-build-standalone@([0-9]+)').Matches.Groups[1].Value

if ([string]::IsNullOrEmpty($VERSION)) {
    Write-Error "Error: Could not extract version from pyproject.toml"
    exit 1
}
if ([string]::IsNullOrEmpty($PYAPP_VERSION)) {
    Write-Error "Error: Could not extract PyApp version from dependabot_hack.yml"
    exit 1
}
if ([string]::IsNullOrEmpty($PYTHON_BUILD_STANDALONE_VERSION)) {
    Write-Error "Error: Could not extract python-build-standalone version from dependabot_hack.yml"
    exit 1
}

$PYAPP_DIST_DIR = ".pyapp/dist/$VERSION"
$PYAPP_BUILD_DIR = ".pyapp/build"
$WAM_FILENAME = "watchmaker-$VERSION-standalone-windows-amd64.exe"

# Python standalone build info - retrieve the latest patch version for Python 3.12
Write-Host "Fetching Python $PYTHON version from python-build-standalone release $PYTHON_BUILD_STANDALONE_VERSION..."
$PYTHON_RELEASE_URL = "https://github.com/astral-sh/python-build-standalone/releases/expanded_assets/$PYTHON_BUILD_STANDALONE_VERSION"
$releaseHtml = Invoke-WebRequest -Uri $PYTHON_RELEASE_URL -UseBasicParsing

# Match pattern: cpython-3.12.X+20251031-x86_64-pc-windows-msvc-install_only_stripped.tar.gz
# Extract just the version number (3.12.X) between "cpython-" and "+20251031"
$pattern = "cpython-($PYTHON\.\d+)\+$PYTHON_BUILD_STANDALONE_VERSION-x86_64-pc-windows-msvc-install_only_stripped\.tar\.gz"
$matches = [regex]::Matches($releaseHtml.Content, $pattern)

if ($matches.Count -gt 0) {
    $PYTHON_FULL_VERSION = $matches[0].Groups[1].Value
} else {
    $PYTHON_FULL_VERSION = ""
}

if ([string]::IsNullOrEmpty($PYTHON_FULL_VERSION)) {
    Write-Host "Failed to find Windows Python distribution."
    Write-Host "Looking for pattern: $pattern"
    Write-Host "Searching for any cpython-3.12 Windows builds:"
    $allMatches = [regex]::Matches($releaseHtml.Content, "cpython-3\.12\.\d+\+$PYTHON_BUILD_STANDALONE_VERSION-x86_64[^`"]*windows[^`"]*\.tar\.gz")
    if ($allMatches.Count -gt 0) {
        Write-Host "Found $($allMatches.Count) Windows builds:"
        $allMatches | Select-Object -First 5 | ForEach-Object { Write-Host "  $($_.Value)" }
    }
    Write-Error "Error: Could not determine Python $PYTHON patch version from release $PYTHON_BUILD_STANDALONE_VERSION"
    exit 1
}

$PYTHON_RELEASE = "cpython-$PYTHON_FULL_VERSION+$PYTHON_BUILD_STANDALONE_VERSION-x86_64-pc-windows-msvc-install_only_stripped.tar.gz"
$PYTHON_URL = "https://github.com/astral-sh/python-build-standalone/releases/download/$PYTHON_BUILD_STANDALONE_VERSION/$PYTHON_RELEASE"

Write-Host "Building PyApp standalone for watchmaker v$VERSION..."
Write-Host "Using PyApp v$PYAPP_VERSION"
Write-Host "Using Python $PYTHON_FULL_VERSION from python-build-standalone"

Write-Host "-----------------------------------------------------------------------"
cargo --version
rustc --version
Write-Host "-----------------------------------------------------------------------"

# Determine extraction tool (prefer tar, fallback to 7z)
$UseTar = $true
$SevenZipPath = "C:\Program Files\7-Zip\7z.exe"

if (Get-Command tar -ErrorAction SilentlyContinue) {
    Write-Host "Using tar for extraction"
} elseif (Test-Path $SevenZipPath) {
    Write-Host "Using 7-Zip at $SevenZipPath"
    $UseTar = $false
} else {
    Write-Error "Error: Neither tar nor 7-Zip is available"
    exit 1
}

# Check for gcc and install if missing
if (-not (Get-Command gcc.exe -ErrorAction SilentlyContinue)) {
    Write-Host "gcc.exe not found, installing mingw via chocolatey..."
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install -y mingw
        # Refresh PATH to pick up newly installed gcc
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Error "Error: gcc.exe is not available and chocolatey is not installed"
        exit 1
    }
}

# Build wheel if dist directory doesn't exist
if (-not (Test-Path "dist")) {
    Write-Host "dist directory not found, building wheel..."
    uv build --wheel
}

# Find the wheel file
$WHEEL_FILE = Get-ChildItem -Path "dist" -Filter "watchmaker-$VERSION-py3-none-any.whl" -Recurse | Select-Object -First 1
if ($null -eq $WHEEL_FILE) {
    Write-Error "Error: Could not find wheel file for version $VERSION"
    exit 1
}
$WHEEL_FILE_ABS = $WHEEL_FILE.FullName
Write-Host "Using wheel: $WHEEL_FILE_ABS"

# Download and prepare custom Python distribution
Write-Host "Downloading Python standalone distribution..."
New-Item -ItemType Directory -Force -Path $PYAPP_BUILD_DIR | Out-Null
$UV_CACHE_PATH = ".pyapp/build/.local-share/uv"
$env:UV_CACHE_DIR = (New-Item -ItemType Directory -Force -Path $UV_CACHE_PATH).FullName
Push-Location $PYAPP_BUILD_DIR

if (-not (Test-Path $PYTHON_RELEASE)) {
    Invoke-WebRequest -Uri $PYTHON_URL -OutFile $PYTHON_RELEASE
}

$PYTHON_DIR = "python"

Write-Host "Extracting Python distribution..."
# Remove existing python directory if it exists
if (Test-Path $PYTHON_DIR) {
    Remove-Item -Recurse -Force $PYTHON_DIR
}
if ($UseTar) {
    tar -xzf $PYTHON_RELEASE
} else {
    # First extract .gz to get .tar
    & $SevenZipPath x $PYTHON_RELEASE -y
    $tarFile = $PYTHON_RELEASE -replace '\.gz$', ''
    # Then extract .tar
    & $SevenZipPath x $tarFile -y
    # Clean up intermediate .tar file
    Remove-Item $tarFile -Force
}

$PYTHON_BIN = Join-Path $PYTHON_DIR "python.exe"

Write-Host "Installing watchmaker and dependencies into custom Python distribution..."
uv pip install --python $PYTHON_BIN $WHEEL_FILE_ABS boto3

Write-Host "Creating custom distribution archive..."
$CUSTOM_DIST = "cpython-$PYTHON_FULL_VERSION-watchmaker-$VERSION.tar.gz"
if ($UseTar) {
    tar -czf $CUSTOM_DIST $PYTHON_DIR
} else {
    & $SevenZipPath a -ttar temp.tar $PYTHON_DIR
    & $SevenZipPath a -tgzip $CUSTOM_DIST temp.tar
    Remove-Item temp.tar -Force
}

Write-Host "Custom distribution created: $CUSTOM_DIST"
Get-Item $CUSTOM_DIST | Format-List Length,FullName

# Build the standalone with PyApp via cargo install
Write-Host "Building PyApp standalone with cargo install..."
Pop-Location
New-Item -ItemType Directory -Force -Path $PYAPP_DIST_DIR | Out-Null

$env:PYAPP_PROJECT_NAME = "watchmaker"
$env:PYAPP_PROJECT_VERSION = $VERSION
$env:PYAPP_DISTRIBUTION_EMBED = "1"
$env:PYAPP_DISTRIBUTION_PATH = (Resolve-Path "$PYAPP_BUILD_DIR/$CUSTOM_DIST").Path
$env:PYAPP_DISTRIBUTION_PYTHON_PATH = "python/python.exe"
$env:PYAPP_FULL_ISOLATION = "1"
$env:PYAPP_SKIP_INSTALL = "1"

# Use a persistent target directory for build cache
$env:CARGO_TARGET_DIR = "$PYAPP_BUILD_DIR/target"
$PYAPP_INSTALL_DIR = "$PYAPP_BUILD_DIR/install"

cargo install pyapp --locked --force --version $PYAPP_VERSION --root $PYAPP_INSTALL_DIR --target-dir $env:CARGO_TARGET_DIR

# Move the binary from cargo install location to final location
$sourceExe = Join-Path $PYAPP_INSTALL_DIR "bin/pyapp.exe"
$destExe = Join-Path $PYAPP_DIST_DIR $WAM_FILENAME

if (Test-Path $destExe) {
    Remove-Item -Force $destExe
}
Move-Item -Path $sourceExe -Destination $destExe

Write-Host "Creating sha256 hashes of standalone binary..."
Push-Location $PYAPP_DIST_DIR
$hash = (Get-FileHash -Algorithm SHA256 $WAM_FILENAME).Hash.ToLower()
"$hash  $WAM_FILENAME" | Out-File -Encoding ASCII -NoNewline "$WAM_FILENAME.sha256"
Get-Content "$WAM_FILENAME.sha256"
Pop-Location

Write-Host "Checking standalone binary version..."
$VERSION_OUTPUT = & (Join-Path $PYAPP_DIST_DIR $WAM_FILENAME) --version
Write-Host $VERSION_OUTPUT

Write-Host "Validating versions..."
if ($VERSION_OUTPUT -notmatch "Watchmaker/$VERSION") {
    Write-Error "Error: Expected Watchmaker version $VERSION, but got: $VERSION_OUTPUT"
    exit 1
}

if ($VERSION_OUTPUT -notmatch "Python/$PYTHON_FULL_VERSION") {
    Write-Error "Error: Expected Python version $PYTHON_FULL_VERSION, but got: $VERSION_OUTPUT"
    exit 1
}

Write-Host "Version validation successful: Watchmaker $VERSION with Python $PYTHON_FULL_VERSION"

Write-Host "Listing files in dist dir..."
Get-ChildItem -Recurse $PYAPP_DIST_DIR | Format-Table -AutoSize
