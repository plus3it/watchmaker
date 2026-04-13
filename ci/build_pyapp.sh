#!/bin/bash
set -eu -o pipefail

PYTHON=3.14

VERSION=$(grep -E '^version\s*=' pyproject.toml | sed 's/^version = "\(.*\)"$/\1/')
PYAPP_VERSION=$(sed -n 's/.*ofek\/pyapp@v//p' .github/workflows/dependabot_hack.yml)

PYAPP_DIST_DIR=".pyapp/dist/${VERSION}"
PYAPP_BUILD_DIR=".pyapp/build"
WAM_FILENAME="watchmaker-${VERSION}-standalone-linux-x86_64"

# Determine the latest available patch version via uv metadata
echo "Fetching latest Python ${PYTHON}.x version from uv..."
PYTHON_FULL_VERSION=$(uv python list "$PYTHON" \
    | grep -oE "${PYTHON//./\\.}\\.[0-9]+" \
    | sort -V \
    | tail -n 1)

if [ -z "$PYTHON_FULL_VERSION" ]; then
    echo "Error: Could not determine latest Python ${PYTHON} patch version from uv"
    exit 1
fi

echo "Building PyApp standalone for watchmaker v${VERSION}..."
echo "Using PyApp v${PYAPP_VERSION}"
echo "Using Python ${PYTHON_FULL_VERSION} from uv"

echo "-----------------------------------------------------------------------"
cargo --version
rustc --version
echo "-----------------------------------------------------------------------"

# Build wheel if dist directory doesn't exist
if [ ! -d "dist" ]; then
    echo "dist directory not found, building wheel..."
    uv build --wheel
fi

# Find the wheel file
WHEEL_FILE=$(find dist -name "watchmaker-${VERSION}-py3-none-any.whl" | head -n 1)
if [ -z "$WHEEL_FILE" ]; then
    echo "Error: Could not find wheel file for version ${VERSION}"
    exit 1
fi
WHEEL_FILE_ABS=$(realpath "$WHEEL_FILE")
echo "Using wheel: $WHEEL_FILE_ABS"

# Prepare custom Python distribution from uv-managed Python
echo "Installing Python ${PYTHON_FULL_VERSION} with uv..."
mkdir -p "$PYAPP_BUILD_DIR"
cd "$PYAPP_BUILD_DIR"
PYTHON_INSTALL_DIR="python"

# Remove any existing python directory to avoid overlapping files
if [ -d "$PYTHON_INSTALL_DIR" ]; then
    rm -rf "$PYTHON_INSTALL_DIR"
fi

uv python install "${PYTHON_FULL_VERSION}" --install-dir "$PYTHON_INSTALL_DIR" --no-bin

PYTHON_DIR=$(find "$PYTHON_INSTALL_DIR" -mindepth 1 -maxdepth 1 -type d -name "cpython-${PYTHON_FULL_VERSION}-*" | head -n 1)
if [ -z "$PYTHON_DIR" ] || [ ! -d "$PYTHON_DIR" ]; then
    echo "Error: Could not find installed Python directory under ${PYTHON_INSTALL_DIR}"
    exit 1
fi

PYTHON_BIN="${PYTHON_DIR}/bin/python${PYTHON}"

echo "Installing watchmaker and dependencies into custom Python distribution..."
export UV_CACHE_DIR="${HOME}/.local/share/uv"
uv pip install --break-system-packages --link-mode copy --python "$PYTHON_BIN" "$WHEEL_FILE_ABS" boto3

echo "Creating custom distribution archive..."
CUSTOM_DIST="cpython-${PYTHON_FULL_VERSION}-watchmaker-${VERSION}.tar.zst"
tar -I zstd -cf "$CUSTOM_DIST" "$PYTHON_DIR"

echo "Custom distribution created: $CUSTOM_DIST"
ls -lh "$CUSTOM_DIST"

# Build the standalone with PyApp via cargo install
echo "Building PyApp standalone with cargo install..."
cd ../..
mkdir -p "$PYAPP_DIST_DIR"

export PYAPP_PROJECT_NAME="watchmaker"
export PYAPP_PROJECT_VERSION="$VERSION"
export PYAPP_DISTRIBUTION_EMBED=1
PYAPP_DISTRIBUTION_PATH="$(realpath "${PYAPP_BUILD_DIR}/${CUSTOM_DIST}")"
export PYAPP_DISTRIBUTION_PATH
export PYAPP_DISTRIBUTION_PYTHON_PATH="${PYTHON_DIR}/bin/python${PYTHON}"
export PYAPP_FULL_ISOLATION=1
export PYAPP_SKIP_INSTALL=1

# Use a persistent target directory for build cache
export CARGO_TARGET_DIR="${PYAPP_BUILD_DIR}/target"
PYAPP_INSTALL_DIR="${PYAPP_BUILD_DIR}/install"

cargo install pyapp --locked --force --version "${PYAPP_VERSION}" --root "${PYAPP_INSTALL_DIR}" --target-dir "${CARGO_TARGET_DIR}"

# Move the binary from cargo install location to final location
if [ "${PYAPP_INSTALL_DIR}/bin/pyapp" -ef "${PYAPP_DIST_DIR}/${WAM_FILENAME}" ]; then
    rm -f "${PYAPP_DIST_DIR}/${WAM_FILENAME}"
fi
mv "${PYAPP_INSTALL_DIR}/bin/pyapp" "${PYAPP_DIST_DIR}/${WAM_FILENAME}"

echo "Creating sha256 hashes of standalone binary..."
(cd "$PYAPP_DIST_DIR"; sha256sum "$WAM_FILENAME" > "${WAM_FILENAME}.sha256")
cat "${PYAPP_DIST_DIR}/${WAM_FILENAME}.sha256"

echo "Setting executable permissions..."
chmod +x "${PYAPP_DIST_DIR}/${WAM_FILENAME}"

echo "Checking standalone binary version..."
VERSION_OUTPUT=$("${PYAPP_DIST_DIR}/${WAM_FILENAME}" --version)
echo "$VERSION_OUTPUT"

echo "Validating versions..."
if ! echo "$VERSION_OUTPUT" | grep -q "Watchmaker/${VERSION}"; then
    echo "Error: Expected Watchmaker version ${VERSION}, but got: $VERSION_OUTPUT"
    exit 1
fi

if ! echo "$VERSION_OUTPUT" | grep -q "Python/${PYTHON_FULL_VERSION}"; then
    echo "Error: Expected Python version ${PYTHON_FULL_VERSION}, but got: $VERSION_OUTPUT"
    exit 1
fi

echo "Version validation successful: Watchmaker ${VERSION} with Python ${PYTHON_FULL_VERSION}"

echo "Listing files in dist dir..."
ls -alRh "$PYAPP_DIST_DIR"
