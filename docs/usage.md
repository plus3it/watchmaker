# Usage

## `watchmaker` from the CLI

```shell
# watchmaker --help
usage: watchmaker [-h] [--version] [-v] [-c CONFIG] [-n] [-l LOG_DIR]
                  [--s3-source] [-s SALT_STATES] [-A ADMIN_GROUPS]
                  [-a ADMIN_USERS] [-t COMPUTER_NAME] [-e ENVIRONMENT]
                  [-p OU_PATH]

optional arguments:
  -h, --help            show this help message and exit
  --version             Print version info.
  -v, --verbose         Enable verbose logging: -v for INFO, -vv to include
                        DEBUG, if option is left out, only WARNINGS and higher
                        are logged.
  -c CONFIG, --config CONFIG
                        Path or URL to the config.yaml file.
  -n, --no-reboot       If this flag is not passed, Watchmaker will reboot the
                        system upon success. This flag suppresses that
                        behavior. Watchmaker suppresses the reboot
                        automatically if it encounters afailure.
  -l LOG_DIR, --log-dir LOG_DIR
                        Path to the log directory for logging.
  --s3-source           Use S3 utilities to retrieve content instead of http/s
                        utilities.
  -s SALT_STATES, --salt-states SALT_STATES
                        Comma-separated string of salt states to apply. A
                        value of 'None' will not apply any salt states. A
                        value of 'Highstate' will apply the salt highstate.
  -A ADMIN_GROUPS, --admin-groups ADMIN_GROUPS
                        Set a salt grain that specifies the domain groups that
                        should have root privileges on Linux or admin
                        privileges on Windows. Value must be a colon-separated
                        string. E.g. "group1:group2"
  -a ADMIN_USERS, --admin-users ADMIN_USERS
                        Set a salt grain that specifies the domain users that
                        should have root privileges on Linux or admin
                        privileges on Windows. Value must be a colon-separated
                        string. E.g. "user1:user2"
  -t COMPUTER_NAME, --computer-name COMPUTER_NAME
                        Set a salt grain that specifies the computername to
                        apply to the system.
  -e ENVIRONMENT, --env ENVIRONMENT
                        Set a salt grain that specifies the environment in
                        which the system is being built. E.g. dev, test, or
                        prod
  -p OU_PATH, --ou-path OU_PATH
                        Set a salt grain that specifies the full DN of the OU
                        where the computer account will be created when
                        joining a domain. E.g.
                        "OU=SuperCoolApp,DC=example,DC=com"
```

## `watchmaker` as EC2 userdata

For **Linux**, you must ensure `pip` is installed, and then you can install
`watchmaker` from PyPi. After that, run `watchmaker` using any option available
on the [CLI](#watchmaker-from-the-cli). Here is an example:

```shell
#!/bin/sh
PYPI_URL=https://pypi.org/simple

# Get the host
PYPI_HOST=$(echo $PYPI_URL |sed -e "s/[^/]*\/\/\([^@]*@\)\?\([^:/]*\).*/\2/")

# Install pip
yum -y --enablerepo=epel install python-pip

# Install watchmaker
pip install --index-url="$PYPI_URL" --trusted-host="$PYPI_HOST" --allow-all-external --upgrade pip setuptools watchmaker

# Run watchmaker
watchmaker -vv --log-dir=/var/log/watchmaker
```

Alternatively, cloud-config directives can also be used on **Linux**:

```yaml
#cloud-config

runcmd:
  - |
    PYPI_URL=https://pypi.org/simple

    # Get the host
    PYPI_HOST=$(echo $PYPI_URL |sed -e "s/[^/]*\/\/\([^@]*@\)\?\([^:/]*\).*/\2/")

    # Install pip
    yum -y --enablerepo=epel install python-pip

    # Install watchmaker
    pip install --index-url="$PYPI_URL" --trusted-host="$PYPI_HOST" --allow-all-external --upgrade pip setuptools watchmaker

    # Run watchmaker
    watchmaker -vv --log-dir=/var/log/watchmaker
```

For **Windows**, the first step is to install Python. `Watchmaker` provides a
simple bootstrap script to do that for you. After installing Python, install
`watchmaker` using `pip` and then run it.

```shell
<powershell>
$BootstrapUrl = "https://raw.githubusercontent.com/plus3it/watchmaker/master/docs/files/bootstrap/watchmaker-bootstrap.ps1"
$PythonUrl = "https://www.python.org/ftp/python/3.6.0/python-3.6.0-amd64.exe"
$PypiUrl = "https://pypi.org/simple"

# Get the host
$PypiHost="$(([System.Uri]$PypiUrl).Host)"

# Download bootstrap file
$BootstrapFile = "${Env:Temp}\$(${BootstrapUrl}.split('/')[-1])"
(New-Object System.Net.WebClient).DownloadFile("$BootstrapUrl", "$BootstrapFile")

# Install python
& "$BootstrapFile" -PythonUrl "$PythonUrl" -Verbose -ErrorAction Stop

# Install watchmaker
pip install --index-url="$PypiUrl" --trusted-host="$PypiHost" --allow-all-external --upgrade pip setuptools watchmaker

# Run watchmaker
watchmaker -vv --log-dir=C:\Watchmaker\Logs
</powershell>
```

## `watchmaker` as a library

```python
import watchmaker

arguments = watchmaker.Arguments()
arguments.config_path = None
arguments.no_reboot = False
arguments.salt_states = 'None'
arguments.s3_source = False

client = watchhmaker.Client(arguments)
client.install()
```

**Note**: This demonstrates only a few of the arguments that are available for
the `watchmaker.Arguments()` object. For details on all arguments, see the
[API Reference](api.md).
