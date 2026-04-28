#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$PYTHON = "3.14"

# Extract versions from project files
$VERSION = (Select-String -Path "pyproject.toml" -Pattern '^version\s*=\s*"([^"]+)"').Matches.Groups[1].Value
$PYAPP_VERSION = (Select-String -Path ".github/workflows/dependabot_hack.yml" -Pattern 'ofek/pyapp@v([0-9.]+)').Matches.Groups[1].Value

if ([string]::IsNullOrEmpty($VERSION)) {
    Write-Error "Error: Could not extract version from pyproject.toml"
    exit 1
}
if ([string]::IsNullOrEmpty($PYAPP_VERSION)) {
    Write-Error "Error: Could not extract PyApp version from dependabot_hack.yml"
    exit 1
}

$PYAPP_DIST_DIR = ".pyapp/dist/$VERSION"
$PYAPP_BUILD_DIR = ".pyapp/build"
$WAM_FILENAME = "watchmaker-$VERSION-standalone-windows-amd64.exe"

# Determine the latest available patch version via uv metadata
Write-Host "Fetching latest Python $PYTHON.x version from uv..."
$PYTHON_ESCAPE = $PYTHON -replace '\.', '\.'
$PYTHON_FULL_VERSION = uv python list $PYTHON 2>&1 |
    Select-String -Pattern "($PYTHON_ESCAPE\.\d+)" |
    ForEach-Object { $_.Matches[0].Groups[1].Value } |
    Sort-Object { [version]$_ } |
    Select-Object -Last 1

if ([string]::IsNullOrEmpty($PYTHON_FULL_VERSION)) {
    Write-Error "Error: Could not determine latest Python $PYTHON patch version from uv"
    exit 1
}

Write-Host "Building PyApp standalone for watchmaker v$VERSION..."
Write-Host "Using PyApp v$PYAPP_VERSION"
Write-Host "Using Python $PYTHON_FULL_VERSION from uv"

Write-Host "-----------------------------------------------------------------------"
cargo --version
rustc --version
Write-Host "-----------------------------------------------------------------------"

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

# Prepare custom Python distribution from uv-managed Python
Write-Host "Installing Python $PYTHON_FULL_VERSION with uv..."
New-Item -ItemType Directory -Force -Path $PYAPP_BUILD_DIR | Out-Null
$UV_CACHE_PATH = ".pyapp/build/.local-share/uv"
$env:UV_CACHE_DIR = (New-Item -ItemType Directory -Force -Path $UV_CACHE_PATH).FullName
Push-Location $PYAPP_BUILD_DIR

$PYTHON_INSTALL_DIR = "python"

# Remove any existing python directory to avoid overlapping files
if (Test-Path $PYTHON_INSTALL_DIR) {
    Remove-Item -Recurse -Force $PYTHON_INSTALL_DIR
}

uv python install $PYTHON_FULL_VERSION --install-dir $PYTHON_INSTALL_DIR --no-bin

$PYTHON_DIR = Get-ChildItem -Path $PYTHON_INSTALL_DIR -Directory -Filter "cpython-${PYTHON_FULL_VERSION}-*" | Select-Object -First 1 -ExpandProperty FullName
if ([string]::IsNullOrEmpty($PYTHON_DIR) -or -not (Test-Path $PYTHON_DIR)) {
    Write-Error "Error: Could not find installed Python directory in $PYTHON_INSTALL_DIR"
    exit 1
}

$PYTHON_BIN = Join-Path $PYTHON_DIR "python.exe"

Write-Host "Installing watchmaker and dependencies into custom Python distribution..."
uv pip install --break-system-packages --link-mode copy --python $PYTHON_BIN $WHEEL_FILE_ABS boto3

Write-Host "Creating custom distribution archive..."
$CUSTOM_DIST = "cpython-$PYTHON_FULL_VERSION-watchmaker-$VERSION.zip"
Compress-Archive -Path $PYTHON_DIR -DestinationPath $CUSTOM_DIST -CompressionLevel Optimal

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
$PYTHON_DIR_LEAF = Split-Path $PYTHON_DIR -Leaf
$env:PYAPP_DISTRIBUTION_PYTHON_PATH = "$PYTHON_DIR_LEAF/python.exe"
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

Write-Host "Copying bootstrap script to dist dirs..."
Copy-Item docs/files/bootstrap/watchmaker-bootstrap.ps1 -Destination "$PYAPP_DIST_DIR"

Write-Host "Listing files in dist dir..."
Get-ChildItem -Recurse $PYAPP_DIST_DIR | Format-Table -AutoSize
