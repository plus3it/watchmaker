$ErrorActionPreference = "Stop"

$VERSION = (Select-String -Path setup.cfg -Pattern '^version = ').Line -replace '^(version = )(.*)$', '$2'

$PYI_DIST_DIR = ".pyinstaller\dist\${VERSION}"
$PYI_SPEC_DIR = ".pyinstaller\spec"
$PYI_WORK_DIR = ".pyinstaller\build"

$PYI_HOOK_DIR = ".\ci\pyinstaller\win"
$PYI_SCRIPT = "${PYI_SPEC_DIR}\watchmaker-standalone.py"
$WAM_SCRIPT = ".\src\watchmaker\__main__.py"
$WAM_FILENAME = "watchmaker-${VERSION}-standalone-windows-amd64"

python -m pip install -r requirements/pip.txt

Write-Host "-----------------------------------------------------------------------"
python --version
python -m pip --version
Write-Host "-----------------------------------------------------------------------"

python -m pip install -r requirements/build.txt
python -m pip install --editable .
python -m pip list

Write-Host "Creating standalone for watchmaker v${VERSION}..."
New-Item -Path "$PYI_SPEC_DIR" -Force -ItemType "directory"
Copy-Item "$WAM_SCRIPT" -Destination "$PYI_SCRIPT"
# Add debug argument to pyinstaller command to build standalone with debug flags
#    --debug all \
pyinstaller --noconfirm --clean --onefile `
    --name "$WAM_FILENAME" `
    --runtime-tmpdir . `
    --paths src `
    --additional-hooks-dir "$PYI_HOOK_DIR" `
    --distpath "$PYI_DIST_DIR" `
    --specpath "$PYI_SPEC_DIR" `
    --workpath "$PYI_WORK_DIR" `
    "$PYI_SCRIPT"

# Uncomment this to list the files in the standalone; can help when debugging
# echo "Listing files in standalone..."
# pyi-archive_viewer --log --brief --recursive "${DIST_DIR}/${WAM_FILENAME}.exe"

Write-Host "Creating sha256 hashes of standalone binary..."
$WAM_HASH = Get-FileHash -Algorithm SHA256 "${PYI_DIST_DIR}\${WAM_FILENAME}.exe"
Set-Content -Path "${PYI_DIST_DIR}\${WAM_FILENAME}.exe.sha256" -Value "$($WAM_HASH.hash) ${WAM_FILENAME}.exe"
Get-Content "${PYI_DIST_DIR}\${WAM_FILENAME}.exe.sha256"

Write-Host "Checking standalone binary version..."
& "${PYI_DIST_DIR}/${WAM_FILENAME}.exe" --version

Write-Host "Copying bootstrap script to dist dirs..."
Copy-Item docs/files/bootstrap/watchmaker-bootstrap.ps1 -Destination "$PYI_DIST_DIR"

Write-Host "Listing files in dist dirs..."
Get-ChildItem -Recurse -Force -Path "${PYI_DIST_DIR}\*"
