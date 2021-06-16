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

call .gravitybee/gravitybee-environs.bat
%GB_ENV_GEN_FILE_W_PATH% --version
