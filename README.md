[![license](https://img.shields.io/github/license/plus3it/watchmaker.svg)](./LICENSE)
[![Build Status](https://travis-ci.org/plus3it/watchmaker.svg)](https://travis-ci.org/plus3it/watchmaker)

# Watchmaker
Watchmaker helps provision a system from its initial installation to its final configuration. It was inspired by a desire to eliminate static system images with embedded configuration settings (e.g., gold disks) and the pain associated with maintaining them.

Watchmaker is a Python package with dependencies on PyYAML to process a configuration file and boto3 to access AWS resources. Watchmaker has been created to work in most OS set-ups that are "STIGable". The tool is being developed as a standalone capability, but can be kicked off during instance creation. Bootstrap scripts are provided in PowerShell, Bash, or Python to 1) install Python (in the case of Windows) and 2) kick-off Watchmaker.

More complex configuration management (CM) environments may be layered in as part of the preparation framework. Salt is used to demonstrate how to layer in a CM tool and build a functioning system hardening capability, but feel free to use any CM tool of your choice.
# Installation
The easiest way to install Watchmaker is to download the egg file from ???. Then install as follows:
```
easy_install <name of egg file>
```
However, if you wish to have the latest and greatest version of Watchmaker, you can run the following command from within the Watchmaker directory:
```
python setup.py bdist_egg
```
This will produce the egg file from which you can install the Watchmaker package and all of its dependencies.
#AWS Userdata
There are 3 scripts available to be ingested as userdata upon the creation of a new EC2 instance. You can use a bash shell script, a Python script, or a PowerShell script.

To find the available bootstrap scripts, go to the following:
```
watchmaker\watchmaker\static\shell\bootstrap
```
If the image you are creating has CentOS or RHEL as its OS, then Python is already installed and you may run a bash shell bootstrap script or a Python bootstrap script.

If the image you are creating has Windows as its OS, then you should run the PowerShell bootstrap script.