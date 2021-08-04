#!/bin/bash
set -eu -o pipefail

export VIRTUAL_ENV_DIR=venv

virtualenv --python=python3 $VIRTUAL_ENV_DIR
source $VIRTUAL_ENV_DIR/bin/activate

python -m pip install -r requirements/pip.txt

echo "-----------------------------------------------------------------------"
python --version
python -m pip --version
echo "-----------------------------------------------------------------------"

python -m pip install -r requirements/build.txt
python -m pip install --editable .
python -m pip list

# creates standalone
gravitybee --src-dir src --sha file --with-latest --extra-data static --extra-data ../vendor/pypa/get-pip/public/2.7 --extra-pkgs boto3 --extra-modules boto3

source .gravitybee/gravitybee-environs.sh
eval "$GB_ENV_GEN_FILE_W_PATH" --version

# Copies windows bootstrap to the gravitybee staging directory
cp docs/files/bootstrap/watchmaker-bootstrap.ps1 "${GB_ENV_STAGING_DIR}/${GB_ENV_APP_VERSION}"
cp docs/files/bootstrap/watchmaker-bootstrap.ps1 "${GB_ENV_STAGING_DIR}/latest"
ls -alR "${GB_ENV_STAGING_DIR}/"*
