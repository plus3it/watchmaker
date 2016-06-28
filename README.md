[![license](https://img.shields.io/github/license/plus3it/watchmaker.svg)](./LICENSE)
[![Build Status](https://travis-ci.org/plus3it/watchmaker.svg)](https://travis-ci.org/plus3it/watchmaker)

# Watchmaker
Watchmaker is a Python package with dependencies on PyYAML (to process a configuration file) and boto3 (to access AWS resources). Watchmaker has been created to work in most OS set-ups that are "STIGable". The tool is being developed as a standalone capability, but can be kicked off during instance creation. Bootstrap scripts are provided in PowerShell, Bash, or Python to 1) install Python (in the case of Windows) and 2) kick-off Watchmaker.

More complex configuration management (CM) environments may be layered in as part of the preparation framework. Salt is used to demonstrate how to layer in a CM tool and build a functioning system hardening capability, but feel free to use any CM tool of your choice.
# Documentation
For information on installing and using Watchmaker, go to https://watchmaker.readthedocs.io.

Alternatively, you can install mkdocs with
 ```
 pip install mkdocs
 ```
 and then in the Watchmaker directory, run
 ```
 mkdocs serve
 ```
 This will start a light-weight server on `http://127.0.0.1:8000` containing the documentation on Watchmaker.
