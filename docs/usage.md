# Usage

## `watchmaker` from the CLI

Once watchmaker is [installed](installation.html) and a
[configuration file](configuration.html) has been created (or you have decided
to use the default configuration), using watchmaker as a CLI utility is as
simple as executing `watchmaker`. Below is the output of `watchmaker --help`,
showing the CLI options.

```shell
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

## `watchmaker` in AWS

### `watchmaker` as EC2 userdata

Calling watchmaker via EC2 userdata is a variation on using it as a CLI
utility. The main difference is that you must account for installing watchmaker
first, as part of the userdata. Since the userdata syntax and dependency
installation differ a bit on Linux and Windows, we provide methods for each as
examples.

.. note::

    The ``pip`` commands in the examples are a bit more complex than
    necessarily needed, depending on your use case. In these examples, we are
    taking into account limitations in FIPS support in the default PyPi repo.
    This way the same ``pip`` command works for all platforms.

#### Linux

For **Linux**, you must ensure `pip` is installed, and then you can install
`watchmaker` from PyPi. After that, run `watchmaker` using any option available
on the [CLI](#watchmaker-from-the-cli). Here is an example:

```shell
#!/bin/sh
PIP_URL=https://bootstrap.pypa.io/get-pip.py
PYPI_URL=https://pypi.org/simple

# Install pip
curl "$PIP_URL" | python - --index-url="$PYPI_URL" wheel==0.29.0

# Install watchmaker
pip install --index-url="$PYPI_URL" --upgrade pip setuptools watchmaker

# Run watchmaker
watchmaker --log-level debug --log-dir=/var/log/watchmaker
```

Alternatively, cloud-config directives can also be used on **Linux**:

```yaml
#cloud-config

runcmd:
  - |
    PIP_URL=https://bootstrap.pypa.io/get-pip.py
    PYPI_URL=https://pypi.org/simple

    # Install pip
    curl "$PIP_URL" | python - --index-url="$PYPI_URL" wheel==0.29.0

    # Install watchmaker
    pip install --index-url="$PYPI_URL" --upgrade pip setuptools watchmaker

    # Run watchmaker
    watchmaker --log-level debug --log-dir=/var/log/watchmaker
```

#### Windows

For **Windows**, the first step is to install Python. `Watchmaker` provides a
simple bootstrap script to do that for you. After installing Python, install
`watchmaker` using `pip` and then run it.

```shell
<powershell>
$BootstrapUrl = "https://raw.githubusercontent.com/plus3it/watchmaker/master/docs/files/bootstrap/watchmaker-bootstrap.ps1"
$PythonUrl = "https://www.python.org/ftp/python/3.6.4/python-3.6.4-amd64.exe"
$PypiUrl = "https://pypi.org/simple"

# Download bootstrap file
$BootstrapFile = "${Env:Temp}\$(${BootstrapUrl}.split('/')[-1])"
(New-Object System.Net.WebClient).DownloadFile("$BootstrapUrl", "$BootstrapFile")

# Install python
& "$BootstrapFile" -PythonUrl "$PythonUrl" -Verbose -ErrorAction Stop

# Install watchmaker
python -m pip install --index-url="$PypiUrl" --upgrade pip setuptools
pip install --index-url="$PypiUrl" --upgrade watchmaker

# Run watchmaker
watchmaker --log-level debug --log-dir=C:\Watchmaker\Logs
</powershell>
```

### `watchmaker` as a CloudFormation template

Watchmaker can be integrated into a CloudFormation template as well. This
project provides a handful of CloudFormation templates that launch instances or
create autoscaling groups, and that install and execute Watchmaker during the
launch. These templates are intended as examples for you to modify and extend
as you need.

.. note::

    Note that the links in this section are intended for viewing the templates
    in a web browser. See the `Direct Downloads`_ section for links to the raw
    files.

#### Cloudformation templates

*   [Linux Autoscale Group][lx-autoscale]
*   [Linux Instance][lx-instance]
*   [Windows Autoscale Group][win-autoscale]
*   [Windows Instance][win-instance]

#### Cloudformation parameter-maps

Sometimes it is helpful to define the parameters for a template in a file, and
pass those to CloudFormation along with the template. We call those "parameter
maps", and provide one for each of the templates above.

*   [Linux Autoscale Params][lx-autoscale-params]
*   [Linux Instance Params][lx-instance-params]
*   [Windows Autoscale Params][win-autoscale-params]
*   [Windows Instance Params][win-instance-params]

[lx-autoscale]: https://github.com/plus3it/terraform-aws-watchmaker/blob/master/modules/lx-autoscale/watchmaker-lx-autoscale.cfn.json
[lx-instance]: https://github.com/plus3it/terraform-aws-watchmaker/blob/master/modules/lx-instance/watchmaker-lx-instance.cfn.json
[win-autoscale]: https://github.com/plus3it/terraform-aws-watchmaker/blob/master/modules/win-autoscale/watchmaker-win-autoscale.cfn.json
[win-instance]: https://github.com/plus3it/terraform-aws-watchmaker/blob/master/modules/win-instance/watchmaker-win-instance.cfn.json

[lx-autoscale-params]: https://github.com/plus3it/terraform-aws-watchmaker/blob/master/modules/lx-autoscale/watchmaker-lx-autoscale.params.cfn.json
[lx-instance-params]: https://github.com/plus3it/terraform-aws-watchmaker/blob/master/modules/lx-instance/watchmaker-lx-instance.params.cfn.json
[win-autoscale-params]: https://github.com/plus3it/terraform-aws-watchmaker/blob/master/modules/win-autoscale/watchmaker-win-autoscale.params.cfn.json
[win-instance-params]: https://github.com/plus3it/terraform-aws-watchmaker/blob/master/modules/win-instance/watchmaker-win-instance.params.cfn.json

### `watchmaker` in Terraform

Watchmaker can also be integrated into a [Terraform framework](https://www.terraform.io/) by directly utilizing the
[Watchmaker AWS Terraform modules](https://github.com/plus3it/terraform-aws-watchmaker) and
passing the required parameters.

#### Terraform Modules

*   [Linux Autoscale Group][dir-lx-autoscale-tf]
*   [Linux Instance][dir-lx-instance-tf]
*   [Windows Autoscale Group][dir-win-autoscale-tf]
*   [Windows Instance][dir-win-instance-tf]

The modules incorporate the CloudFormation templates within their respective Terraform templates so
they become deployable and manageable from within the Terraform cli.

.. note::

   * Each corresponding Terraform template and the CloudFormation template are grouped together
     in the same directory.

   * The links in this section are intended for viewing the templates
     in a web browser. See the `Direct Downloads`_ section for links to the raw
     files.

Variables can be input interactively via the Terraform console or
directly to the Terraform module. An example Terraform file that calls the
lx-autoscale module is shown below.

```
provider "aws" {}

module "test-lx-instance" {
  source = "git::https://github.com/plus3it/terraform-aws-watchmaker//modules/lx-instance/"

  Name      = "tf-watchmaker-lx-autoscale"
  AmiId     = "__AMIID__"
  AmiDistro = "__AMIDISTRO__"
}
```
#### Additional Watchmaker Terraform examples

*   [Linux Autoscale Group](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/examples/lx-autoscale)
*   [Linux Instance](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/examples/lx-instance)
*   [Windows Autoscale Group](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/examples/win-autoscale)
*   [Windows Instance](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/examples/win-instance)

## `watchmaker` in Azure

### `watchmaker` as Custom Script Extension

Custom Script Extension downloads and executes scripts on Azure virtual machines.
For Linux, you run the bash script shown in the section on [Linux](#linux). You can
store the bash script in Azure Storage or a publicly available url (such as with S3).
Then you execute the stored script with a command. For example, a JSON string could contain
```json
{
  "fileUris": ["https://path-to-bash-script/run_watchmaker.sh"],
  "commandToExecute": "./run_watchmaker.sh"
}
```
These parameters can be passed in via Azure CLI or within a Resource Management Template.
For more in-depth information, see Microsoft's
[documentation](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/extensions-customscript).

For Windows, you would execute a PowerShell script in a similar manner as for [Windows](#windows)
(but without the powershell tags). Then you would have the following parameters:
```json
{
  "fileUris": ["https://path-to-bash-script/run_watchmaker.ps1"],
  "commandToExecute": "powershell -ExecutionPolicy Unrestricted -File run_watchmaker.ps1"
}
```
For more in-depth information on using Custom Script Extension for Windows, see Microsoft's
[documentation](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/extensions-customscript).

## `watchmaker` as a library

Watchmaker can also be used as a library, as part of another python
application.

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

.. note::

    This demonstrates only a few of the arguments that are available for the
    ``watchmaker.Arguments()`` object. For details on all arguments, see the
    :any:`API Reference <api>`.

## Direct downloads

The following links can be used for directly fetching (e.g., via `curl`,
`wget`, etc.) resources previously noted on this page:

### Cloudformation Files

|CFN Template Files|CFN Parameter Files|
|--------------|---------------|
|[Linux AutoScale][raw-lx-autoscale]|[Linux Autoscale][raw-lx-autoscale-params]|
|[Linux Instance][raw-lx-instance]|[Linux Instance][raw-lx-instance-params]|
|[Windows Autoscale][raw-win-autoscale]|[Windows Autoscale][raw-win-autoscale-params]|
|[Windows Instance][raw-win-instance]|[Windows Instance][raw-win-instance-params]|

[raw-lx-autoscale]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-autoscale/watchmaker-lx-autoscale.cfn.json
[raw-lx-instance]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-instance/watchmaker-lx-instance.cfn.json
[raw-win-autoscale]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-autoscale/watchmaker-win-autoscale.cfn.json
[raw-win-instance]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-instance/watchmaker-win-instance.cfn.json

[raw-lx-autoscale-params]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-autoscale/watchmaker-lx-autoscale.params.cfn.json
[raw-lx-instance-params]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-instance/watchmaker-lx-instance.params.cfn.json
[raw-win-autoscale-params]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-autoscale/watchmaker-win-autoscale.params.cfn.json
[raw-win-instance-params]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-instance/watchmaker-win-instance.params.cfn.json

[dir-lx-autoscale-tf]: https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/lx-autoscale
[dir-lx-instance-tf]: https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/lx-instance
[dir-win-autoscale-tf]: https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/win-autoscale
[dir-win-instance-tf]: https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/win-instance

### Terraform Files

|TF Main Files|TF Variables Files|TF Outputs Files|
|--------------|---------------|---------------|
|[Linux AutoScale][raw-lx-autoscale-tf]|[Linux AutoScale][raw-var-lx-autoscale-tf]|[Linux AutoScale][raw-out-lx-autoscale-tf]|
|[Linux Instance][raw-lx-instance-tf]|[Linux Instance][raw-var-lx-instance-tf]|[Linux Instance][raw-out-lx-instance-tf]|
|[Windows Autoscale][raw-win-autoscale-tf]|[Windows Autoscale][raw-var-win-autoscale-tf]|[Windows Autoscale][raw-out-win-autoscale-tf]|
|[Windows Instance][raw-win-instance-tf]|[Windows Instance][raw-var-win-instance-tf]|[Windows Instance][raw-out-win-instance-tf]|

[raw-lx-autoscale-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-autoscale/main.tf
[raw-lx-instance-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-instance/main.tf
[raw-win-autoscale-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-autoscale/main.tf
[raw-win-instance-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-instance/main.tf

[raw-var-lx-autoscale-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-autoscale/variables.tf
[raw-var-lx-instance-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-instance/variables.tf
[raw-var-win-autoscale-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-autoscale/variables.tf
[raw-var-win-instance-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-instance/variables.tf

[raw-out-lx-autoscale-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-autoscale/outputs.tf
[raw-out-lx-instance-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/lx-instance/outputs.tf
[raw-out-win-autoscale-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-autoscale/outputs.tf
[raw-out-win-instance-tf]: https://raw.githubusercontent.com/plus3it/terraform-aws-watchmaker/master/modules/win-instance/outputs.tf
