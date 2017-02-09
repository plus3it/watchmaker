# Usage

## `watchmaker` from the CLI:

```shell
# watchmaker --help
usage: watchmaker [-h] [--version] [-v] [-c CONFIG] [-n] [--log-dir LOG_DIR]
                  [--sourceiss3bucket] [-s SALTSTATES] [-A ADMINGROUPS]
                  [-a ADMINUSERS] [-t COMPUTERNAME] [-e ENTENV] [-p OUPATH]

optional arguments:
  -h, --help            show this help message and exit
  --version             Print version info.
  -v                    Enable verbose logging: -v for INFO, -vv to include
                        DEBUG, if option is left out, only WARNINGS and higher
                        are logged.
  -c CONFIG, --config CONFIG
                        Path or URL to the config.yaml file.
  -n, --noreboot        If this flag is not passed, Watchmaker will reboot the
                        system upon success. This flag suppresses that
                        behavior. Watchmaker suppresses the reboot
                        automatically if it encounters afailure.
  --log-dir LOG_DIR     Path to the log directory for logging.
  --sourceiss3bucket    Use S3 utilities to retrieve content instead of http/s
                        utilities.
  -s SALTSTATES, --saltstates SALTSTATES
                        Comma-separated string of salt states to apply. A
                        value of 'None' will not apply any salt states. A
                        value of 'Highstate' will apply the salt highstate.
  -A ADMINGROUPS, --admingroups ADMINGROUPS
                        Set a salt grain that specifies the domain groups that
                        should have root privileges on Linux or admin
                        privileges on Windows. Value must be a colon-separated
                        string. E.g. "group1:group2"
  -a ADMINUSERS, --adminusers ADMINUSERS
                        Set a salt grain that specifies the domain users that
                        should have root privileges on Linux or admin
                        privileges on Windows. Value must be a colon-separated
                        string. E.g. "user1:user2"
  -t COMPUTERNAME, --computername COMPUTERNAME
                        Set a salt grain that specifies the computername to
                        apply to the system.
  -e ENTENV, --entenv ENTENV
                        Set a salt grain that specifies the environment in
                        which the system is being built. E.g. dev, test, or
                        prod
  -p OUPATH, --oupath OUPATH
                        Set a salt grain that specifies the full DN of the OU
                        where the computer account will be created when
                        joining a domain. E.g.
                        "OU=SuperCoolApp,DC=example,DC=com"
```

## `watchmaker` as a library:

```python
import watchmaker

arguments = watchmaker.Arguments()
arguments.config_path = None
arguments.noreboot = False
arguments.saltstates = 'None'
arguments.sourceiss3bucket = False

client = watchhmaker.Client(arguments)
client.install()
```

**Note**: This demonstrates only a few of the arguments that are available for
the `watchmaker.Arguments()` object. For details on all arguments, see the
[API Reference](api.md).
