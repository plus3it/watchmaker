```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Dissecting The `config.yaml` File

The stock config.yaml file has five top-level directives or directive-maps:

- `watchmaker_version`
- `all`
- `linux`
- `windows`
- `status`

These directives or directive-dictionaries are used to govern the overall behavior of watchmaker's execution. See the [default config.yaml](https://raw.githubusercontent.com/plus3it/watchmaker/main/src/watchmaker/static/config.yaml) file for generic layout and exemplar-content.

## The `watchmaker_version` Directive

This directive applies a compatibility-filter to the watchmaker execution. If the installed version of watchmaker doesn't meet the version-critera set by this line, watchmaker won't work with this file's content. It's assumed that any watchmaker version that does not match the version-criteria will not (properly) support the configuration directives. Normally, the version is set as "greater than or equal to" string.

## The `all` Map

This map is used to supply default values to both saltstack and to specific SaltStack formulae. The map-keys most likely to be of interest will be:

- `valid_environments`
- `salt_content`
- `salt_states`
- `salt_version`
- `user_formulas`

### The `valid_environments` List-Parameter

This list provides a list of names of "environments" that saltstack's site-customization behavior has been configured to deliver. This will typically be used by environments that wish to customize deployments on an environment-by-environment basis (e.g. where an organization's development, testing/integration and production environments might have different endpoints to contact for things like configuring authentication) and wish to have a single `config.yaml` file to be used across all valid deployment-environments.

_Typical_ values will be `null`,`dev`, `test` and/or `prod`.

- Usage of `null` indicates no differentiation between environments &ndash; that the generic configuration should be applied. This can mean that all the environments leverage the same service-integration information or that each deployment-environment will be governed by a different `config.yaml` file.
- The others are shorthand for "development", "testing & integration" and "production", respectively.

The word "typical" was previously emphasized because _any_ value (other than `null`) is supported so long as there is a correspondingingly-named content-hierarchy in the site's custom Salt-content archive file (see the `salt-content` dictionary-key in the next section). This content-hierarchy needs to exist within the Salt-content archive file at `./pillar/<ENVIRONMENT_NAME>` (e.g., a `dev` environment would have a corresponding `./pillar/dev` directory in the Salt-content archive file).

```{eval-rst}
.. note::
    The default environment that watchmaker will apply is specified using the
    ``environment`` parameter. In the example, this is set to ``null`` --
    meaning that a generic configuration will be applied. This value is
    overridden by requesting a specific environment-configuration by using
    either ``-e <ENVIRONMENT>`` or ``--env <ENVIRONMENT>`` flag and argument
    when invoking watchmaker (per the :doc:`Usage Guide </usage>`).
```

### The `salt_content` String-Parameter

This string defines where Watchmaker should attempt to download any site-customization content from. If this value is the literal `null`, watchmaker will not attempt to download any site-customization content. Otherwise, a valid URI pointing to a customized Salt-content archive should be used. This URI can point to a locally-staged file, an HTTP/HTTPS URL or an S3 URI.

If using an S3 URI, a couple of further requirements apply:

- When installing watchmaker, it will be necessary for the `boto3` Python library to be installed
- The to-be-configured system must have read access to the specified S3 URI

By default, `watchmaker` will extract this archive-file's contents at `/srv/watchmaker/salt` (Linux) or `C:\Watchmaker\Salt\srv` (Windows) the `./` referenced elsewhere in this document will be relative to that extraction-location.

```{eval-rst}
.. note::
    See the :doc:`Salt Contents Archive File <SaltContent>` document for a
    discussion on the contents and layout of this file.
```

### The `salt_states` String-Parameter

This parameter is by Watchmaker to invoke SaltStack with the desired states selected for execution. The typical value for this parameter is `Highstate`. The `Highstate` value tells watchmaker to invoke SaltStack with the `Highstate` invoker rather than iterated-states invoker. Invoking Saltstack with the `Highstate` invoker  will cause all available and activated formulas to be selected for execution.

### The `salt_version` String-Parameter

The value for this parameter instructs watchmaker which version of the Saltstack software it should download &ndash; or, if the correct version is already installed, skip re-downloading or re-installing. This will correspond to the value returned when `salt-call --version` is executed (after the `watchmaker` utility has downloaded and installed SaltStack). See the watchmaker [changelog](https://watchmaker.readthedocs.io/en/stable/changelog.html) for guidance on latest supported version of Saltstack.

### The `user_formulas` Dictionary-Parameter

This dictionary-parameter usually has no content. However, if one wishes to customize watchmaker's execution either by adding further formulae to install or to override installtion of default-formulae's contents with newer content (e.g., when testing updates to standard formulae), this dictionary should be populated. The expected value will take the form of:

```yaml
      <FORMULA_NAME>: <DOWNLOAD_URL>
```

- `<FORMULA_NAME>` will be used as the installation-location for the formula-contents into the `/srv/watchmaker/salt/formulas` (Linux) or `C:\Watchmaker\Salt\srv\formulas` (Windows) directories.
- `<DOWNLOAD_URL>` will be used as the location from which to download an archive of target formula's content. This content should be in the form of a ZIP archive. Most frequently, this will be the public download-URL of a GitHub branch's (or commit-ID's) ZIP-archived, but any archive-URL that watchmaker has permission to download _should_ work

For example, if one is working on updates to the `ash-linux-formula` and has made those changes in a GitHub project, one would specify a value of:

```yaml
      ash-linux-formula: https://github.com/<USER_ID>/<PROJECT_NAME>/archive/refs/heads/<BRANCH_NAME>.zip
```

The above will cause the content normally loaded at `.../formulas/ash-linux-formula` to be replaced with the content unarchved from the `https://github.com/<USER_ID>/<PROJECT_NAME>/archive/refs/heads/<BRANCH_NAME>.zip` archive-URI.

Similarly, if one is working on a _new_ formula, specifying:

```yaml
      <NEW_FORMULA_NAME>: https://github.com/<USER_ID>/<PROJECT_NAME>/archive/refs/heads/<BRANCH_NAME>.zip
```

Will cause the content-archive hosted at the specified GitHub URL to be unarcheved at the platform-appropriate `.../formulas/<NEW_FORMULA_NAME>` directory-path. It _should_ also cause an appropriate update to the SaltStack minion-configuration[^1]. If this fails to happen, there is most likely a formatting issue with your `user_formulas` declaration. The following is (a snippet of) how the declaration _should_ look:

```yaml
all:
  salt:
    [...elided...]
    user_formulas:
      <FORMULA_NAME>: <SOURCE_URL>
```

Note that the `<FORMULA_NAME>` line is indented two spaces from the `user_formulas` token. If improper indentation is used - for example:

```yaml
all:
  salt:
    [...elided...]
    user_formulas:
    <FORMULA_NAME>: <SOURCE_URL>
```

Neither the `.../formulas/<NEW_FORMULA_NAME>` directory-path will be created nor the `minion` file updated.


## The `linux` Map

This map contains two top-level keys: `yum` and `salt`. Both are also maps.

The `yum` map instructs watchmaker about where to fetch `yum`/`dnf` repository-definition files from. Using the `yum:repo_map`, watchmaker will perform a lookup using the `dist:<distribution>` value and `el_version` value to identify the download `url` from which to pull the appropriate  `yum`/`dnf` repository-definition files from


```{eval-rst}
.. note::
    Currently, mappings for ``Red Hat 7``, ``CentOS 7``, ``Alma Linux 8``,
    ``CentOS 8 Stream``, ``Oracle Linux 8``, ``Red Hat 8`` and ``Rocky Linux 8``
    are defined. Further Enterprise Linux distributions may be supported by
    appropriate extension of this map, along with further modifcations to a few
    Saltstack formulae.
```

The `salt` map is generally not modified for customization or other activities.


## The `windows` Map

Similar to the `linux` map, the `windows` map instructs watchmaker about where to fetch the Salt-minion setup-executable for Windows from.

As with the `linux` map, the `salt` dictionary is generally not modified for customization or other activities.

## The `status` Map

This map defines the "status" content that watchmaker will attempt to write as a tag to the watchmaker-managed host. Currently, only Amazon EC2s and Azure VMs are supported. Currently, this map defaults to a value of:

```yaml
status:
  providers:
    - key: WatchmakerStatus
      required: false
      provider_type: aws
    - key: WatchmakerStatus
      required: false
      provider_type: azure
```

The watchmaker finish/status routines interpret the above to mean, "apply the tag named `WatchmakerStatus` to the managed-host and set an appropriate completion-status value[^2], but do not exit with an error if the tagging-operation fails".

[^1]: The minion-configuration file is found at `/opt/watchmaker/salt/minion` on Linux hosts and `C:\Watchmaker\Salt\conf\minion` on Windows hosts.
[^2]: The completion-status tagger will set a value of either `Completed` or `Error`.
