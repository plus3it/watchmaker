```{eval-rst}
.. image:: images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Usage

## `watchmaker` from the CLI

Once Watchmaker is [installed](installation) and a
[configuration file](configuration) has been created (or you have decided
to use the default configuration), using Watchmaker as a CLI utility is as
simple as executing `watchmaker`. Below is the output of `watchmaker --help`,
showing the CLI options.

In addition to the below options, any setting supported by the [configfiguration file](configuration)
can be passed on the CLI. Some settings from the configuration file are not listed
in the `--help` output, which displays only the most frequently used options. To
pass any such "hidden" CLI argument, just precede it with `--` and convert an
underscore to a dash. For example, to pass the `salt_content` argument on the CLI,
use `watchmaker <other options> --salt-content <content-url>`. Arguments passed
on the CLI always override the corresponding setting in the configuration file
(see [configuration](configuration) for precedence).

```console
# watchmaker --help
Usage: watchmaker [OPTIONS]

  Entry point for Watchmaker cli.

Options:
  --version                       Show the version and exit.
  -c, --config TEXT               Path or URL to the config.yaml file.
  -l, --log-level [info|debug|critical|warning|error]
                                  Set the log level. Case-insensitive.
  -d, --log-dir DIRECTORY         Path to the directory where Watchmaker log
                                  files will be saved.
  -n, --no-reboot                 If this flag is not passed, Watchmaker will
                                  reboot the system upon success. This flag
                                  suppresses that behavior. Watchmaker
                                  suppresses the reboot automatically if it
                                  encounters a failure.
  -s, --salt-states TEXT          Comma-separated string of salt states to
                                  apply. A value of 'None' will not apply any
                                  salt states. A value of 'Highstate' will
                                  apply the salt highstate.
  --s3-source                     Use S3 utilities to retrieve content instead
                                  of http/s utilities. Boto3 must be
                                  installed, and boto3 credentials must be
                                  configured that allow access to the S3
                                  bucket.
  -A, --admin-groups TEXT         Set a salt grain that specifies the domain
                                  groups that should have root privileges on
                                  Linux or admin privileges on Windows. Value
                                  must be a colon-separated string. E.g.
                                  "group1:group2"
  -a, --admin-users TEXT          Set a salt grain that specifies the domain
                                  users that should have root privileges on
                                  Linux or admin privileges on Windows. Value
                                  must be a colon-separated string. E.g.
                                  "user1:user2"
  -t, --computer-name TEXT        Set a salt grain that specifies the
                                  computername to apply to the system.
  -e, --env TEXT                  Set a salt grain that specifies the
                                  environment in which the system is being
                                  built. E.g. dev, test, or prod
  -p, --ou-path TEXT              Set a salt grain that specifies the full DN
                                  of the OU where the computer account will be
                                  created when joining a domain. E.g.
                                  "OU=SuperCoolApp,DC=example,DC=com"
  --help                          Show this message and exit.
```


## `watchmaker` as a standalone package (Beta feature)

*Standalone packages are a beta feature and may not function in all
environments.*

Once a Watchmaker standalone executable has been
[downloaded](installation) and a
[configuration file](configuration) has been created (or you have decided
to use the default configuration), use Watchmaker similarly to the CLI
utility.

For example, on Linux, you can view the CLI options (shown above) using
the same flag.

```console
# ./watchmaker --help
```

From Windows, similarly, execute Watchmaker by running it from the command line:

```ps1con
PS C:\wam> watchmaker.exe --help
```

## `watchmaker` in AWS

### `watchmaker` as EC2 userdata

Calling Watchmaker via EC2 userdata is a variation on using it as a CLI
utility. The main difference is that you must account for installing Watchmaker
first, as part of the userdata. Since the userdata syntax and dependency
installation differ a bit on Linux and Windows, we provide methods for each as
examples.

```{eval-rst}
.. note::

    The ``pip`` commands in the examples are a bit more complex than
    necessarily needed, depending on your use case. In these examples, we are
    taking into account limitations in FIPS support in the default PyPi repo.
    This way the same ``pip`` command works for all platforms.
```

#### Linux

For **Linux**, you must ensure `pip` is installed, and then you can install
`watchmaker` from PyPi. After that, run `watchmaker` using any option available
on the [CLI](#watchmaker-from-the-cli). Here is an example:

```shell
#!/bin/sh
PYPI_URL=https://pypi.org/simple

# Setup terminal support for UTF-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Install pip
python3 -m ensurepip

# Install setup dependencies
python3 -m pip install --index-url="$PYPI_URL" --upgrade pip setuptools

# Install Watchmaker
python3 -m pip install --index-url="$PYPI_URL" --upgrade watchmaker

# Run Watchmaker
watchmaker --log-level debug --log-dir=/var/log/watchmaker
```

Alternatively, cloud-config directives can also be used on **Linux**:

```yaml
#cloud-config

runcmd:
  - |
    PYPI_URL=https://pypi.org/simple

    # Setup terminal support for UTF-8
    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8

    # Install pip
    python3 -m ensurepip

    # Install setup dependencies
    python3 -m pip install --index-url="$PYPI_URL" --upgrade pip setuptools

    # Install Watchmaker
    python3 -m pip install --index-url="$PYPI_URL" --upgrade watchmaker

    # Run Watchmaker
    watchmaker --log-level debug --log-dir=/var/log/watchmaker
```

#### Windows

For **Windows**, the first step is to install Python. `Watchmaker` provides a
simple bootstrap script to do that for you. After installing Python, install
`watchmaker` using `pip` and then run it.

```shell
<powershell>
$BootstrapUrl = "https://watchmaker.cloudarmor.io/releases/latest/watchmaker-bootstrap.ps1"
$PythonUrl = "https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe"
$PypiUrl = "https://pypi.org/simple"

# Download bootstrap file
$BootstrapFile = "${Env:Temp}\$(${BootstrapUrl}.split('/')[-1])"
(New-Object System.Net.WebClient).DownloadFile("$BootstrapUrl", "$BootstrapFile")

# Install python
& "$BootstrapFile" -PythonUrl "$PythonUrl" -Verbose -ErrorAction Stop

# Install Watchmaker
python -m pip install --index-url="$PypiUrl" --upgrade pip setuptools
pip install --index-url="$PypiUrl" --upgrade watchmaker

# Run Watchmaker
watchmaker --log-level debug --log-dir=C:\Watchmaker\Logs
</powershell>
```

### `watchmaker` as a CloudFormation template

Watchmaker can be integrated into a CloudFormation template as well. This
project provides a handful of CloudFormation templates that launch instances or
create autoscaling groups, and that install and execute Watchmaker during the
launch. These templates are intended as examples for you to modify and extend
as you need.

Sometimes it is helpful to define the parameters for a template in a file, and
pass those to CloudFormation along with the template. We call those "parameter
maps", and provide one for each of the CFN templates.

#### Cloudformation templates

*   [Linux Autoscale Group][dir-lx-autoscale]
*   [Linux Instance][dir-lx-instance]
*   [Windows Autoscale Group][dir-win-autoscale]
*   [Windows Instance][dir-win-instance]

### `watchmaker` in a Terraform module

Watchmaker can also be used with [Terraform](https://www.terraform.io/) by
utilizing the [Watchmaker AWS Terraform modules](https://github.com/plus3it/terraform-aws-watchmaker)
and passing the required parameters.

#### Terraform Modules

*   [Linux Autoscale Group][dir-lx-autoscale]
*   [Linux Instance][dir-lx-instance]
*   [Windows Autoscale Group][dir-win-autoscale]
*   [Windows Instance][dir-win-instance]

```{eval-rst}
.. note::

   Each corresponding Terraform module and CloudFormation template are
   grouped together in the same directory.
```

The CloudFormation templates are integrated within their respective Terraform
module, so they become deployable and manageable from within the Terraform cli.

Variables can be input interactively via the Terraform console or directly to
the Terraform module. An example Terraform file that calls the `lx-autoscale`
module is shown below.

```terraform
provider "aws" {}

module "test-lx-instance" {
  source = "git::https://github.com/plus3it/terraform-aws-watchmaker//modules/lx-instance/"

  Name      = "tf-watchmaker-lx-autoscale"
  AmiId     = "__AMIID__"
  AmiDistro = "__AMIDISTRO__"
}
```

#### Additional Watchmaker Terraform examples

*   [Linux Autoscale Example](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/examples/lx-autoscale)
*   [Linux Instance Example](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/examples/lx-instance)
*   [Windows Autoscale Example](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/examples/win-autoscale)
*   [Windows Instance Example](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/examples/win-instance)

[dir-lx-autoscale]: https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/lx-autoscale
[dir-lx-instance]: https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/lx-instance
[dir-win-autoscale]: https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/win-autoscale
[dir-win-instance]: https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/win-instance

## `watchmaker` in Azure

### `watchmaker` as Custom Script Extension

Custom Script Extension downloads and executes scripts on Azure virtual
machines. For Linux, you run the bash script shown in the section on
[Linux](#linux). You can store the bash script in Azure Storage or a publicly
available url (such as with S3). Then you execute the stored script with a
command. For example, a JSON string could contain

```json
{
  "fileUris": ["https://path-to-bash-script/run_watchmaker.sh"],
  "commandToExecute": "./run_watchmaker.sh"
}
```

These parameters can be passed in via Azure CLI or within a Resource Management
Template. For more in-depth information, see Microsoft's
[documentation on Linux](https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-linux).

For Windows, you would execute a PowerShell script in a similar manner as for
[Windows](#windows) (but without the powershell tags). Then you would have the
following parameters:

```json
{
  "fileUris": ["https://path-to-bash-script/run_watchmaker.ps1"],
  "commandToExecute": "powershell -ExecutionPolicy Unrestricted -File run_watchmaker.ps1"
}
```

For more in-depth information on using Custom Script Extension for Windows, see
Microsoft's [documentation on Windows](https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-windows).

## `watchmaker` as a library

Watchmaker can also be used as a library, as part of another python
application.

```python
import watchmaker

arguments = watchmaker.Arguments()
arguments.config_path = None
arguments.no_reboot = False
arguments.salt_states = None
arguments.s3_source = False

client = watchhmaker.Client(arguments)
client.install()
```

```{eval-rst}
.. note::

   This demonstrates only a few of the arguments that are available for the
   ``watchmaker.Arguments()`` object. For details on all arguments, see the
   :any:`API Reference <api>`.
```
