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

Watchmaker comes with a default config.yaml file:

```
Linux:
  Yum:
    Parameters:
      yumrepomap:
        #Amazon:
        - dist: amazon
          url: https://s3.amazonaws.com/systemprep-repo/linux/yum.repos/systemprep-repo-amzn.repo
        #CentOS:
        - dist: centos
          url: https://s3.amazonaws.com/systemprep-repo/linux/yum.repos/systemprep-repo-centos.repo
        #RedHat:
        - dist: redhat
          url: https://s3.amazonaws.com/systemprep-repo/linux/yum.repos/systemprep-repo-rhel.repo
        #SaltEL6:
        - dist: all
          epel_version: 6
          url: https://s3.amazonaws.com/systemprep-repo/linux/yum.repos/systemprep-repo-salt-el6.repo
        #SaltEL7:
        - dist: all
          epel_version: 7
          url: https://s3.amazonaws.com/systemprep-repo/linux/yum.repos/systemprep-repo-salt-el7.repo

  Salt:
    Parameters:
      admingroups: None
      adminusers: None
      computername: None
      entenv: False
      user_formulas:
        #To add other formulas, make sure it is a url to a zipped file as follows:
        #- https://s3.amazonaws.com/salt-formulas/systemprep-formula-master.zip
        #- https://s3.amazonaws.com/salt-formulas/ash-linux-formula-master.zip
        #To "overwrite" submodule formulas, make sure name matches submodule names.
      formulaterminationstrings:
        - -master
        - -latest
      oupath: None
      salt_debug_log: None
      salt_results_log: None
      saltbootstrapsource: None
      saltcontentsource: https://s3.amazonaws.com/systemprep-content/linux/salt/salt-content.zip
      saltinstallmethod: yum
      saltgitrepo: None
      saltstates: Highstate
      saltversion: None
      sourceiss3bucket: False

Windows:
  Salt:
    Parameters:
      admingroups: None
      adminusers: None
      ashrole: MemberServer
      computername: None
      entenv: False
      user_formulas:
        #To add other formulas, make sure it is a url to a zipped file as follows:
        #- https://s3.amazonaws.com/salt-formulas/systemprep-formula-master.zip
        #To "overwrite" submodule formulas, make sure name matches submodule names.
        - https://s3.amazonaws.com/salt-formulas/dotnet4-formula-master.zip
      formulaterminationstrings:
        - -master
        - -latest
      oupath: None
      salt_debug_log: None
      salt_results_log: None
      saltcontentsource: https://s3.amazonaws.com/systemprep-content/windows/salt/salt-content.zip
      saltinstallerurl: https://s3.amazonaws.com/systemprep-repo/windows/salt/Salt-Minion-2015.8.5-AMD64-Setup.exe
      saltstates: Highstate
      saltworkingdir: SystemContent\Windows\Salt\
      sourceiss3bucket: False
```

The parent node is either `Linux` or `Windows` and it identifies the parameters to use for that particular OS.
The next level identifies tools to use within the OS. For `Linux`, Watchmaker will use `yum` and `Salt`, while
`Windows` just requires parameters for `Salt` commands.

After the command nodes, Watchmaker identifies all of the parameters needed for a successful run of those nodes.
Each paramter in the `config.yaml` file are also paramters that can be set at the CLI level.

You can create a file using the above format with your own set of standard values and use that file
for Watchmaker.  You just need to set the CLI parameter `--config` to point to that file.
