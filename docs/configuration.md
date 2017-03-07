# Configuration

Watchmaker is configured using a YAML file. To understand YAML, read up on it
[here][0].

Watchmaker comes with a default [config.yaml][1] file, which should work
out-of-the-box. You can also use it as an example to create your own
configuration file.

The configuration is a dictionary. The parent nodes (keys) are `all`, `linux`,
or `windows`. The parent nodes contain a list of workers to execute, and each
worker contains parameters specific to that worker. The `all` node is applied
to every system, and `linux` and `windows` are applied only to their respective
systems.

You can create a file using the above format with your own set of standard
values and use that file for Watchmaker. Pass the CLI parameter `--config` to
point to that file.

## Config.yaml Parent Nodes

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

## Config.yaml Worker Nodes

### salt

Parameters supported by the Salt Worker:

-   `admin_groups` (_list_): The group(s) that you would like the admin accounts
    placed within.
-   `admin_users` (_list_): The user(s) that would be created as admins.
-   `computer_name` (_string_): The computer or hostname that should be applied.
-   `environment` (_string_): Set for the environment in which the system is
    being built.
-   `formula_termination_strings` (_list_): Strings to remove from the end of a
    salt formula zip archive. The defaults are common branch or tag names when
    a salt formula is hosted on GitHub. If a user has a salt formula with a
    different convention, additional strings to match can be defined. For
    example:

    ```
    Salt formula name: `systemprep-formula`
    User-defined formula zip filename: `systemprep-formula-homemade.zip`

    formula_termination_strings:
      - -master
      - -latest
      - -homemade

    The termination string `-homemade` should be added, so that the default
    formula is overridden properly.
    ```

-   `ou_path` (_string_): Specifies the full DN of the OU where the computer
    account will be created when joining a domain.

    ```yaml
    ou_path: "OU=Super Cool App,DC=example,DC=com"
    ```

-   `salt_states` (_string, comma-separated_): User-defined salt states to apply.

    ```yaml
    salt_states: foo,bar
    ```

-   `s3_source` (_boolean_): Use S3 utilities to retrieve content instead of
    http(s) utilities. For S3 utilities to work, the system must have boto
    credentials configured that allow access to the S3 bucket.
-   `user_formulas` (_list_): URL(s) for user-defined Salt formulas.
-   `salt_debug_log` (_string_): Path to the debug logfile that salt will write
    to.
-   `content_source` (_string_): URL to the Salt content file that contains
    further configuration specific to the salt install.
-   `install_method` (_string_): (Linux-only) The method used to install Salt.
    Currently supports: `yum`, `git`
-   `bootstrap_source` (_string_): (Linux-only) URL to the salt bootstrap
    script. This is required if `install_method` is set to `git`.
-   `git_repo` (_string_): (Linux-only) URL to the salt git repo. This is
    required if `install_method` is set to `git`.
-   `salt_version` (_string_): (Linux-only) A git reference present in
    `git_repo`, such as a commit or a tag. If not specifid, the HEAD of the
    default branch will be used.
    `installer_url` (_string_): (Windows-only) URL to the Salt Minion installer
    for Windows.

### yum (linux-only)

Parameters supported by the Yum Worker:

-   `repo_map` (list of maps): There be dragons here! Please be careful making
    changes to the default config. Thoroughly test your configuration. The
    default config specifies yum repos that contain the salt-minion. If the
    default repos are not included, and the salt-minion is not available, the
    Salt Worker will fail. You can add repos here that you would like enabled,
    but be wary of removing the default repos. Each map must contain the
    following keys:

    -   `dist` (_list_): Distributions that would install this repo. Some repos
        are supported by multiple distros. (Currently supported distros are
        redhat, centos, and amazon.)
    -   `el_version` (`_string_`): The Enterprise Linux version for this repo,
        as in el6 or el7. Expected values are `'6'` or `'7'`.
    -   `url` (_string_): URL location of the repo file to be added to the
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

## Example config.yaml

```yaml
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
```

[0]: http://www.yaml.org/spec/1.2/spec.html
[1]: https://github.com/plus3it/watchmaker/blob/develop/src/watchmaker/static/config.yaml
