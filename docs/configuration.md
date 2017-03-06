# Configuration

Watchmaker is configured using a YAML file. To understand YAML, read up on it [here][0].

Watchmaker comes with a default [config.yaml][1] file, which should work out-of-the-box. You can also use it as an example to create your own configuration file.

The configuration is a dictionary. The parent nodes (keys) are `all`, `linux`, or `windows`. The parent nodes contain a list of workers to execute, and each worker contains parameters specific to that worker. The `all` node is applied to every system, and `linux` and `windows` are applied only to their respective systems.

You can create a file using the above format with your own set of standard values and use that file for Watchmaker. Pass the CLI parameter `--config` to point to that file.

[0]: http://www.yaml.org/spec/1.2/spec.html
[1]: https://github.com/plus3it/watchmaker/blob/develop/src/watchmaker/static/config.yaml

# Config.yaml
## All

Section for configurations that affect the deployment of the system that are Operating System agnostic.


### Salt

The salt user defined parameters.

|Option | Type | Description|
|-------|:-----:|------------|
|admin_groups: | (list) | The group(s) that you would like the admin accounts placed.|
|admin_users: | (list) |  The user(s) that would be created as admins.  |
|computer_name: | (string) | The computer or hostname that should be applied. |
| environment: | (boolean) |Set for the environment in which the system is being built. </br> `environment: dev`|
|formula_termination_strings: | (list) | The defaults are the typical salt formula naming convention. If a user has a salt formula that deviates from the standard naming conventions in Salt, additional strings to match can be defined. </br> Example: Salt default package: `systemprep-formula` </br>User defined package: `systemprep-formula-homemade.zip` </br>The termination string `-homemade` should be added, so that the default formula is overridden properly. |
| ou_path: | (String) | Specifies the full DN of the OU where the computer account will be created when joining a domain. </br>`ou_path: "OU=Super Cool App, DC=example,DC=com"`|
| salt_state: | (String) comma seperated | User defined salt states. </br>`salt_state: Highstate, Userstate` |
|  s3_source: | (string) | Use S3 utilities to retrieve content instead of http(s) utilities. For S3 utilities to work, the system must have boto credentials configured that allow access to the S3 bucket.|
| user_formulas: | (list) | URL(s) for user defined Salt formulas. |

## Linux
Section for configurations that affect the deployment of the system that are only applicable to Linux based systems.

### Yum

|Option | Type | Description|
|------|:----:|-----|
|repo_map: | Add Section |There be dragons here!</br>Please becareful making changes to the existing repos unless you are sure of what you are doing. You can add repos here that you would like enabled but be weary of changing the existing. Select the EL version that an additional repo should be added to. Then add a full block, redhat and centos are the only supported 'enterprise linux' distros currently supported. Must include dist, el_version, and url|
|dist: |(String) | Distributions that would install this repo. Some repos are supported by multiple distros. (Currently supported distros are redhat, centos, and amazon) |
|el_version:| (6 or 7)| The EL version you are installing a yum repo for. |
|url: | (String) | URL location of the repo to be added to the system.|

Example:
```
repo_map:
  - dist:
      - redhat
      - centos
  el_version: 6
  url: http://someplace.com/my.repo
```

### Salt

Salt configurations that pertain to linux operating system configurations.

|Option | Type | Description|
|-------|:-----:|------------|
|salt_debug_log:| (String) | Path to the debug logfile that should be used for Salt.|
|content_source:| (String) | URL for the location of the Salt content file to be used during installation for the Linux OS|
|install_method: | (String) | The method used to install Salt. (Currently supported: yum, git) |
|bootstrap_source: | (String) | URL to the salt bootstrap script.</br>This is required if `install_method: git`|
|git_repo: | (String) | URL to the salt git repo.</br>This is required if `install_method: git`|
|salt_version: | (String) | A git reference present in `git repo`, such as a commit or a tag. If not specifid, the HEAD of the default branch will be used.|


## Windows

Section for configurations that affect the deployment of the system that are only applicable to Windows based systems.

### Salt

Salt configurations that pertain to Windows operating system configurations.

|Option | Type | Description|
|-------|:-----:|------------|
| salt_debug_log:| (String) | Path to the debug logfile that should be used for Salt.|
| content_source:| (String) | URL for the location of the Salt content file to be used during installation for the Windows OS|
| installer_url: | (String) | URL for the location of the Salt Minion Executable to install for the Windows OS |
| ash_role: | (String) |  |





## Example config.yaml
```
all:
  - salt:
      admin_groups: None
      admin_users: None
      computer_name: None
      environment: False
      formula_termination_strings:
        - -master
        - -latest
      ou_path: None
      salt_states: Highstate
      s3_source: False
      user_formulas:
        #To add other formulas, make sure it is a url to a zipped file as follows:
        #- https://s3.amazonaws.com/salt-formulas/systemprep-formula-master.zip
        #- https://s3.amazonaws.com/salt-formulas/ash-linux-formula-master.zip
        #To "overwrite" submodule formulas, make sure name matches submodule names.

linux:
  - yum:
      repo_map:
        #SaltEL6:
        - dist:
            - redhat
            - centos
          el_version: 6
          url: https://s3.amazonaws.com/systemprep-repo/linux/saltstack/salt/yum.repos/salt-reposync-el6.repo
        - dist: amazon
          el_version: 6
          url: https://s3.amazonaws.com/systemprep-repo/linux/saltstack/salt/yum.repos/salt-reposync-amzn.repo
        #SaltEL7:
        - dist:
            - redhat
            - centos
          el_version: 7
          url: https://s3.amazonaws.com/systemprep-repo/linux/saltstack/salt/yum.repos/salt-reposync-el7.repo
  - salt:
      salt_debug_log: None
      content_source: https://s3.amazonaws.com/systemprep-content/linux/salt/salt-content.zip
      install_method: yum
      bootstrap_source: None
      git_repo: None
      salt_version: None

windows:
  - salt:
      salt_debug_log: None
      content_source: https://s3.amazonaws.com/systemprep-content/windows/salt/salt-content.zip
      installer_url: https://s3.amazonaws.com/systemprep-repo/windows/salt/Salt-Minion-2016.11.2-AMD64-Setup.exe
      ash_role: MemberServer
```
