#!/bin/bash
set -eu -o pipefail

export VIRTUAL_ENV_DIR=venv

VERSION=$(grep "version =" setup.cfg | sed 's/^.*= //')

DIST_DIR="dist/${VERSION}"
DIST_LATEST="dist/latest"
PYI_DIR="ci/pyinstaller"
PYI_SCRIPT="src/watchmaker/__main__.py"
WAM_FILENAME="watchmaker-${VERSION}-standalone-linux-x86_64"
WAM_LATEST="watchmaker-latest-standalone-linux-x86_64"

virtualenv --python=python3 $VIRTUAL_ENV_DIR
source "${VIRTUAL_ENV_DIR}/bin/activate"

python -m pip install -r requirements/pip.txt

echo "-----------------------------------------------------------------------"
python --version
python -m pip --version
echo "-----------------------------------------------------------------------"

python -m pip install -r requirements/build.txt
python -m pip install --editable .
python -m pip list

echo "Creating standalone for watchmaker v${VERSION}..."
# Add debug argument to pyinstaller command to build standalone with debug flags
#    --debug all \
pyinstaller --noconfirm --clean --onefile \
    --name "$WAM_FILENAME" \
    --runtime-tmpdir . \
    --paths src \
    --additional-hooks-dir "$PYI_DIR" \
    --specpath "$PYI_DIR" \
    --distpath "$DIST_DIR" \
    "$PYI_SCRIPT"

# Uncomment this to list the files in the standalone; can help when debugging
# echo "Listing files in standalone..."
# pyi-archive_viewer --log --brief --recursive "${DIST_DIR}/${WAM_FILENAME}"

mkdir -p "dist/latest"
cp "${DIST_DIR}/${WAM_FILENAME}" "${DIST_LATEST}/${WAM_LATEST}"

echo "Creating sha256 hashes of standalone binary..."
(cd "$DIST_DIR"; sha256sum "$WAM_FILENAME" > "${WAM_FILENAME}.sha256")
(cd "$DIST_LATEST"; sha256sum "$WAM_LATEST" > "${WAM_LATEST}.sha256")

echo "Checking standalone binary version..."
eval "${DIST_DIR}/${WAM_FILENAME}" --version

echo "Copying bootstrap script to dist dirs..."
cp docs/files/bootstrap/watchmaker-bootstrap.ps1 "$DIST_DIR"
cp docs/files/bootstrap/watchmaker-bootstrap.ps1 "$DIST_LATEST"

echo "Listing files in dist dirs..."
ls -alRh "$DIST_DIR"/* "$DIST_LATEST"/*
