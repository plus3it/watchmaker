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
watchmaker --help

usage: watchmaker [-h] [--noreboot] [--sourceiss3bucket] [--config CONFIG]
             [--logger] [--log-path LOG_PATH] [--saltstates SALTSTATES]

optional arguments:
  -h, --help            show this help message and exit
  --noreboot            No reboot after provisioning.
  --sourceiss3bucket    Use S3 buckets instead of internet locations for
                        files.
  --config CONFIG       Path or URL to the config.yaml file.
  --saltstates SALTSTATES
                        Define the saltstates to use. Must be 'None', 'Highstate',
                        or 'comma-seperated-string'
  --log-dir             Path to the log directory for logging.
  -vv                   Level of debugging: -v for INFO, -vv to include DEBUG,
                        if option is left out, only WARNINGS and higher are logged.

```

## config.yaml

To understand the yaml markup language, read up on it at http://www.yaml.org/spec/1.2/spec.html.

Watchmaker comes with a default [config.yaml](https://github.com/plus3it/watchmaker/blob/develop/src/watchmaker/static/config.yaml) file.

The parent nodes/keys are `All`, `Linux` or `Windows` and they identify parameters to use for all OSes and for particular OS.
The next level identifies tools to use. For `Linux`, Watchmaker will use `yum`, while `Salt` is used for all OSes.

After the command nodes/keys, Watchmaker identifies all of the parameters needed for a successful run of those nodes.
Each parameter in the `config.yaml` file are also parameters that can be set at the CLI level.

You can create a file using the above format with your own set of standard values and use that file
for Watchmaker.  You just need to set the CLI parameter `--config` to point to that file.
