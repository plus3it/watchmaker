#!/bin/bash
set -eu -o pipefail

export VIRTUAL_ENV_DIR=.pyinstaller/venv

PYTHON=python3.12

VERSION=$(grep -E '^version\s*=' pyproject.toml | sed 's/^version = "\(.*\)"$/\1/')

PYI_DIST_DIR=".pyinstaller/dist/${VERSION}"
PYI_SPEC_DIR=".pyinstaller/spec"
PYI_WORK_DIR=".pyinstaller/build"

PYI_HOOK_DIR="./ci/pyinstaller/elx"
PYI_SCRIPT="${PYI_SPEC_DIR}/watchmaker-standalone.py"
WAM_SCRIPT="./src/watchmaker/__main__.py"
WAM_FILENAME="watchmaker-${VERSION}-standalone-linux-x86_64"

$PYTHON -m venv "$VIRTUAL_ENV_DIR"
# shellcheck disable=SC1091
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
mkdir -p "$PYI_SPEC_DIR"
cp "$WAM_SCRIPT" "$PYI_SCRIPT"
# Add debug argument to pyinstaller command to build standalone with debug flags
#    --debug all \
pyinstaller --noconfirm --clean --onefile \
    --name "$WAM_FILENAME" \
    --runtime-tmpdir . \
    --paths src \
    --additional-hooks-dir "$PYI_HOOK_DIR" \
    --distpath "$PYI_DIST_DIR" \
    --specpath "$PYI_SPEC_DIR" \
    --workpath "$PYI_WORK_DIR" \
    "$PYI_SCRIPT"

# Uncomment this to list the files in the standalone; can help when debugging
# echo "Listing files in standalone..."
# pyi-archive_viewer --log --brief --recursive "${DIST_DIR}/${WAM_FILENAME}"

echo "Creating sha256 hashes of standalone binary..."
(cd "$PYI_DIST_DIR"; sha256sum "$WAM_FILENAME" > "${WAM_FILENAME}.sha256")
cat "${PYI_DIST_DIR}/${WAM_FILENAME}.sha256"

echo "Checking standalone binary version..."
eval "${PYI_DIST_DIR}/${WAM_FILENAME}" --version

echo "Copying bootstrap script to dist dirs..."
cp docs/files/bootstrap/watchmaker-bootstrap.ps1 "$PYI_DIST_DIR"

echo "Listing files in dist dirs..."
ls -alRh "$PYI_DIST_DIR"/*
