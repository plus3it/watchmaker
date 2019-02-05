#!/bin/bash

export VIRTUAL_ENV_DIR=venv

virtualenv $VIRTUAL_ENV_DIR
source $VIRTUAL_ENV_DIR/bin/activate

pip install -r requirements/pip.txt
echo "-----------------------------------------------------------------------"
python --version
pip --version
echo "-----------------------------------------------------------------------"
pip install -r requirements/build.txt
pip install --editable .

# creates standalone
gravitybee --src-dir src --sha file --with-latest --extra-data static --extra-pkgs boto3 --extra-modules boto3
