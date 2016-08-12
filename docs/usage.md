# Usage

To use `watchmaker` in a project::

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

To use `watchmaker` from the CLI::

```
Watchmaker.py --help

usage: Watchmaker.py [-h] [--noreboot] [--sourceiss3bucket] [--config CONFIG]
             [--logger] [--log-path LOG_PATH] [--saltstates SALTSTATES]

optional arguments:
  -h, --help            show this help message and exit
  --noreboot            No reboot after provisioning.
  --sourceiss3bucket    Use S3 buckets instead of internet locations for
                        files.
  --config CONFIG       Path or URL to the config.yaml file.
  --logger              Use stream logger for debugging.
  --log-path LOG_PATH   Path to the logfile for stream logging.
  --saltstates SALTSTATES
                        Define the saltstates to use. Must be 'None', 'Highstate',
                        or 'comma-seperated-string'

```
