python -m pip install -r requirements/pip.txt

echo "-----------------------------------------------------------------------"
python --version
python -m pip --version
echo "-----------------------------------------------------------------------"

; Remove when addressed: https://github.com/plus3it/gravitybee/issues/486
git rm pyproject.toml

python -m pip install -r requirements/build.txt
python -m pip install --editable .
python -m pip list

; creates standalone
gravitybee --src-dir src --sha file --with-latest --extra-data static --extra-data _vendor/pypa/get-pip/public/2.7 --extra-pkgs boto3 --extra-modules boto3

git restore --staged pyproject.toml
git restore pyproject.toml

call .gravitybee/gravitybee-environs.bat
%GB_ENV_GEN_FILE_W_PATH% --version
