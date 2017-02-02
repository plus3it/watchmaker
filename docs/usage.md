# Usage

## `watchmaker` from the CLI:

```shell
watchmaker --help

usage: watchmaker [-h] [--noreboot] [--sourceiss3bucket] [--config CONFIG]
                  [--saltstates SALTSTATES] [--log-dir LOG_DIR] [-v]

optional arguments:
  -h, --help            show this help message and exit
  --noreboot            No reboot after provisioning.
  --sourceiss3bucket    Use S3 buckets instead of internet locations for
                        files.
  --config CONFIG       Path or URL to the config.yaml file.
  --saltstates SALTSTATES
                        Define the saltstates to use. Must be None, Highstate,
                        or a comma-separated-string
  --log-dir LOG_DIR     Path to the log directory for logging.
  -v                    Enable verbose logging: -v for INFO, -vv to include
                        DEBUG, if option is left out, only WARNINGS and higher
                        are logged.
```

## `watchmaker` as a library:

```python
from watchmaker import PrepArguments, Prepare

arguments = PrepArguments()
arguments.noreboot = False
arguments.s3 = False
arguments.config_path = None
arguments.stream = False
arguments.log_path = False
arguments.saltstates = False

systemprep = Prepare(arguments)
systemprep.install_system()
```
