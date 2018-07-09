#!/bin/bash

export VIRTUAL_ENV_DIR=venv

virtualenv $VIRTUAL_ENV_DIR
source $VIRTUAL_ENV_DIR/bin/activate

echo "-----------------------------------------------------------------------"
python --version
pip --version
echo "-----------------------------------------------------------------------"
pip install -r requirements/deploy.txt
pip install --editable .

# creates standalone 
gravitybee --src-dir src --sha file --with-latest --extra-data static --verbose
