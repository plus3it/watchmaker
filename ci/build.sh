#!/bin/bash

export VIRTUAL_ENV_DIR=venv

python3 -m ensurepip --upgrade --default-pip
python3 -m pip install -r requirements/pip.txt
python3 -m pip --version

python3 -m pip install -r requirements/basics.txt
python3 -m pip list

virtualenv --python=python3 $VIRTUAL_ENV_DIR
source $VIRTUAL_ENV_DIR/bin/activate

python -m pip install -r requirements/pip.txt
echo "-----------------------------------------------------------------------"
python --version
pip --version
echo "-----------------------------------------------------------------------"
python -m pip install -r requirements/build.txt
python -m pip install --editable .
python -m pip list

# creates standalone
gravitybee --src-dir src --sha file --with-latest --extra-data static --extra-data ../vendor/pypa/get-pip/2.6 --extra-pkgs boto3 --extra-modules boto3
