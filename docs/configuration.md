```{eval-rst}
.. image:: images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```

<br>

# Configuration

Watchmaker is configured using a [YAML][0] file. Watchmaker's default
[config.yaml][1] file should work out-of-the-box for most systems and
environments. You can also use it as an example to create your own
configuration file. The default config file will install Salt and use the
bundled Salt formulas to harden the system according to the DISA STIG.

The configuration is a dictionary. The parent nodes (keys) are: `all`, `linux`,
or `windows`. The parent nodes contain a list of workers to execute, and each
worker contains parameters specific to that worker. The `all` node is applied
to every system, and `linux` and `windows` are applied only to their respective
systems.

You can create a file using the above format with your own set of standard
values and use that file for Watchmaker. Pass the CLI parameter `--config` to
point to that file.

## Configuration Precedence

In addition to passing values in the configuration file, watchmaker supports
passing arguments on the [cli](usage). The order of precedence for arguments is,
from least to most:

* configuration file
* cli argument

In other words, providing a value as a cli argument will override the same value
provided in the configuration file.

## config.yaml Parent Nodes

### watchmaker_version

If used, this optional node constrains the version of Watchmaker that can be used with the configuration. The `watchmaker_version` node is recommended for all configurations used with versions of Watchmaker 0.17+.

This is an example of using the `watchmaker_version` node:

```yaml
watchmaker_version: "== 0.17.0"
```

Any [PEP440-compatible version specifier](https://www.python.org/dev/peps/pep-0440/#version-specifiers) can be used in the `watchmaker_version` node. Each version clause should include a comparison operator, such as `~=`, `==`, `!=`, `<=`, `>=`, `<`, `>`, or `===`. Multiple clauses can be included, separated by commas. Below are examples of version specifiers.

```yaml
watchmaker_version: "~= 0.17.0"
watchmaker_version: "> 0.16.5"
watchmaker_version: ">= 0.17.0, <= 0.18.9, != 0.17.2"
```

Attempting to use a configuration with an incompatible version of Watchmaker will result in an error.

### all

Section for Worker configurations that affect the deployment of all platforms.
The `all` section will override parameters that are set in the OS-specific
sections of config.yaml.

### linux

Section for Worker configurations that should only be applied to Linux-based
systems.

### windows

Section for Worker configurations that should only be applied to Windows-based
systems.

### status

Watchmaker supports posting the watchmaker status to status providers. Watchmaker status values are one of: 'Running', 'Failed', or 'Completed'. Each status provider defines what it means to "post the status". Currently, the supported provider types include: 'aws' and 'azure'. These status providers both post the status as a tag to the instance/VM.

Providers have the ability to detect whether the system is compatible with the
provider type. In order to post status, the system running watchmaker must be compatible
with the status provider type. For example, the 'azure' provider will be skipped
when watchmaker is running on an AWS EC2 instance, and vice versa.

See the [installation](installation) page for prerequisites for using this feature.

* `IAM Role and Policy` An AWS Role and Policy that allows the instance to create tags must be attached to the instance.  The minimal policy below has been tested in commercial and govcloud.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "ec2:CreateTags",
            "Resource": "arn:<PARTITION>:ec2:<REGION>:<ACCOUNT_ID>:instance/${ec2:InstanceID}",
            "Condition": {
                "StringLike": {
                    "ec2:SourceInstanceARN": "arn:<PARTITION>:ec2:<REGION>:<ACCOUNT_ID>:instance/${ec2:InstanceID}"
                }
            }
        }
    ]
}
```

* `Policy` Policy that allows adding or replacing tag on resource see [Microsoft Azure Tag Policy](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-policies) for more info.

```{eval-rst}
.. note::

    Note: Support for the 'azure' status provider is provisional. If you use it and encounter problems, please open an issue on the GitHub repository!
```

Parameters supported by status

* `providers` ((list of maps)): List of providers

  * `key` (_string_): Status key to use e.g. `WatchmakerStatus`
  * `required` (_boolean_): Required status, when `True` and provider_type is detected, watchmaker raises an error if unable to update status
  * `provider_type` (_string_): Environment provider type e.g. `aws` or `azure`

  Example:

    ```yaml
    status:
      providers:
        - key: 'WatchmakerStatus'
          required: False
          provider_type: 'aws'
        - key: 'WatchmakerStatus'
          required: False
          provider_type: 'azure'
    ```

## Config.yaml Worker Nodes

Watchmaker includes the _workers_ listed below. See the corresponding sections
for details on their configuration parameters.

* [salt](#salt-worker)
* [yum (linux-only)](#yum-worker-linux-only)

### salt worker

Parameters supported by the Salt Worker:

* `admin_groups` (_list_): The group(s) that you would like the admin accounts
    placed within.

* `admin_users` (_list_): The user(s) that would be created as admins.

* `computer_name` (_string_): The computer or hostname that should be applied.

* `environment` (_string_): Set for the environment in which the system is
    being built.

* `valid_environments` (_list_): The list of environments considered valid
    for the environment parameter.

* `ou_path` (_string_): Specifies the full DN of the OU where the computer
    account will be created when joining a domain.

    ```yaml
    ou_path: "OU=Super Cool App,DC=example,DC=com"
    ```

* `pip_install` (_list_): The Python package(s) that formulas require.

    ```yaml
    pip_install:
        - hvac
        - numpy
    ```

* `pip_args` (_list_): Options to pass to salt `pip.install` when installing python packages. See the [salt docs][3] for all options.

    ```yaml
    linux:
      - salt:
          pip_args:
            - pre_releases=True
    ```

* `pip_index` (_string_): Base URL of Python Package Index.

* `salt_states` (_string, comma-separated_): User-defined salt states to
    apply.

    ```yaml
    salt_states: highstate,foo,bar
    ```

* `exclude_states` (_string, comma-separated_): States to exclude from
    execution of salt states.

* `user_formulas` (_dict_): Map of formula names and URLs to zip archives of
    salt formulas. These formulas will be downloaded, extracted, and added to
    the salt file roots. The zip archive must contain a top-level directory
    that, itself, contains the actual salt formula. To "overwrite" bundled
    submodule formulas, make sure the formula name matches the submodule name.

    ```yaml
    user_formulas:
      foo-formula: https://path/to/foo.zip
    ```

* `salt_debug_log` (_string_): Path to the debug logfile that salt will write
    to.

* `salt_content` (_string_): URL to the Salt content file that contains
    further configuration specific to the salt install.

* `salt_content_path` (_string_): The path within the Salt content file
    specified using `salt_content` where salt files are located.
    Can be used to provide the path within the archive file where
    the Salt configuration files are located.

* `install_method` (_string_): (Linux-only) The method used to install Salt.
    Currently supports: `yum`, `git`

* `bootstrap_source` (_string_): (Linux-only) URL to the salt bootstrap
    script. This is required if `install_method` is set to `git`.

* `git_repo` (_string_): (Linux-only) URL to the salt git repo. This is
    required if `install_method` is set to `git`.

* `salt_version` (_string_): (Linux-only) A git reference present in
    `git_repo`, such as a commit or a tag. If not specifid, the HEAD of the
    default branch will be used.

* `installer_url` (_string_): (Windows-only) URL to the Salt Minion installer
    for Windows.

### yum worker (linux-only)

Parameters supported by the Yum Worker:

* `repo_map` (list of maps): There be dragons here! Please be careful making
    changes to the default config. Thoroughly test your configuration. The
    default config specifies yum repos that contain the salt-minion. If the
    default repos are not included, and the salt-minion is not available, the
    Salt Worker will fail. You can add repos here that you would like enabled,
    but be wary of removing the default repos. Each map must contain the
    following keys:

  * `dist` (_list_): Distributions that would install this repo. Some repos
        are supported by multiple distros. (Currently supported distros are
        redhat, centos, and amazon.)
  * `el_version` (`_string_`): The Enterprise Linux version for this repo,
        as in el6 or el7. Expected values are `'6'` or `'7'`.
  * `url` (_string_): URL location of the repo file to be added to the
        system. This file will be copied to `/etc/yum.repos.d/`

    Example:

    ```yaml
    repo_map:
      - dist:
          - redhat
          - centos
        el_version: 6
        url: http://someplace.com/my.repo
    ```

## Downloading config files from Amazon S3

Watchmaker has support for downloading files from Amazon S3. This is useful for
implementations where parts of the Watchmaker config are hosted privately. In order
to use this feature, be sure the necessary prerequisites are installed (see the
[installation page](installation)).

This feature simply uses the "S3 URL" of the object in the S3 bucket. Such URLs
take the form: `s3://<bucket>/<key>`. For example, if you wanted to host a custom
config and custom salt content, you could include the salt-content S3 URL in your
Watchmaker config:

```yaml
all:
  - salt:
      salt_content: s3://path/to/salt-content.zip
```

And then call Watchmaker on the CLI with the `--config` argument:

```console
watchmaker --config s3://path/to/config.yaml
```

## Example config.yaml

This example can be used to construct your own `config.yaml` file. The
[Cloudarmor repo][2] provides yum repo definitions and installers for a few salt
versions.

```yaml
watchmaker_version: ">= 0.24.0.dev"
all:
  - salt:
      admin_groups: null
      admin_users: null
      computer_name: null
      environment: null
      ou_path: null
      salt_content: null
      salt_states: Highstate
      user_formulas:
        # To add extra formulas, specify them as a map of
        #    <formula_name>: <archive_url>
        # The <formula_name> is the name of the directory in the salt file_root
        # where the formula will be placed. The <archive_url> must be a zip
        # file, and the zip must contain a top-level directory that, itself,
        # contains the actual salt formula. To "overwrite" submodule formulas,
        # make sure <formula_name> matches submodule names. E.g.:
        #ash-linux-formula: https://s3.amazonaws.com/salt-formulas/ash-linux-formula-master.zip
        #scap-formula: https://s3.amazonaws.com/salt-formulas/scap-formula-master.zip

linux:
  - yum:
      repo_map:
        #SaltEL6:
        - dist:
            - redhat
            - centos
          el_version: 6
          url: https://watchmaker.cloudarmor.io/yum.defs/saltstack/salt/2019.2.8/salt-reposync-el6.repo
        - dist: amazon
          el_version: 6
          url: https://watchmaker.cloudarmor.io/yum.defs/saltstack/salt/2019.2.8/salt-reposync-amzn.repo
        #SaltEL7:
        - dist:
            - redhat
            - centos
          el_version: 7
          url: https://watchmaker.cloudarmor.io/yum.defs/saltstack/salt/3004.2/salt-reposync-el7-python3.repo
  - salt:
      salt_debug_log: null
      install_method: yum
      bootstrap_source: null
      git_repo: null
      salt_version: null

windows:
  - salt:
      salt_debug_log: null
      installer_url: https://watchmaker.cloudarmor.io/repo/saltstack/salt/windows/Salt-Minion-3004.2-1-Py3-AMD64-Setup.exe

status:
  providers:
    - key: 'WatchmakerStatus'
      required: False
      provider_type: 'aws'
    - key: 'WatchmakerStatus'
      required: False
      provider_type: 'azure'
```

[0]: https://yaml.org/spec/1.2/spec.html
[1]: https://github.com/plus3it/watchmaker/blob/main/src/watchmaker/static/config.yaml
[2]: https://watchmaker.cloudarmor.io/list.html
[3]: https://docs.saltproject.io/en/latest/ref/modules/all/salt.modules.pip.html#salt.modules.pip.install
