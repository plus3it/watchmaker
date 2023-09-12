```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```

<br>

# Salt Contents Archive File

The SallStack contents archive contains three main file-hierarchies

- `pillar`
- `states`
- `winrepo`

## The `pillar` Directory-Tree

This directry-hierarchy contains the pillar-data that is used to govern the behavior of executed SaltStack states. If modifying SaltStack states' behavior from their defaults (or supplying mandatory parameters), place the modifications under this directory-hierarchy.

Any automation-formulae that make reference to Pillar data &ndash; typically such formulae will include a `pillar.example` or `pillar.example.yml` in their content-root directory &ndash; may have their behavior modified through content under this directory-tree. Typically, this directory-tree will contain a `common` directory-tree and a directory-tree for each supported deployment environment. Thus, if one is creating behavioral-controls for `dev`, `test` and `prod` [environments](#the-pillar-directory-tree), the `pillar` directory tree will contain:

- [`common` directory](#the-common-directory-tree)
- `dev` directory
- `prod` directory
- `test` directory

Each formula that should be executed for a given site and environment should reference each formula's previously-mentioned `pillar.example` or `pillar.example.yml` files. Relevant content should be placed into either the `common` directory's `init.sls` files or in the environment-specific `init.sls` files. See below discussions for which directories should be used for a given method of setting parameter values.

In addition, the top-level directory will contain a `top.sls` and (optionally) a `map.jinja` file. These files help Watchmaker's SaltStack components know what further content to execute.

### The `top.sls` file

The `top.sls` file-content will typically look like (taken from the [watchmaker-salt-content](https://github.com/plus3it/watchmaker-salt-content) project's [`pillar/top.sls`](https://raw.githubusercontent.com/plus3it/watchmaker-salt-content/master/pillar/top.sls) file):

```yaml
base:
  'G@os_family:RedHat':
    - common.ash-linux
    - common.scap.elx

  'G@os_family:Windows':
    - common.ash-windows
    - common.netbanner
    - common.scap.windows
    - common.winrepo
```

What this content does is selects a base set of Saltstack pillar-data to read in. This makes execution-customizations of selected saltstack formulae available for those formulae to consume. In the base-scenario (shown above), SaltStack will use the executing system's `os_family` to select which pillar-content to read in. Reading in only platform-relevant content helps reduce the amount of content that Saltstack has to read in.

```{eval-rst}
.. note::
    This value can be queried-for/verified on a host with watchmaker installed by executing:

        ``salt-call -c /opt/watchmaker/salt/ --output text grains.get os_family``

    On an Enterprise Linux system, this will produce:

        ``local: RedHat``
```

If further execution-customization content is desired to be made available to executing formulae, it may be set up here.

## The `map.jinja` file

The presence/use of a `map.jinja` file is optional in the `pillar` root-directory. Any `map.jinja` file within the `pillar` _hierarchy_ is designed to facilitate the loading of pillar data. The primary reason for having a `map.jinja` within the `pillar` root-directory is if there's common pillar data that needs to be shared across environments. If there's a need for such shared content, the pillar subdirectories would reference the shared file at `/map.jinja` (typically, if they reference a `map.jinja` file, at all, they will reference their "local" version by pointing at `map.jinja`).

### The `common` Directory-Tree

As the name suggest, this directory-tree contains parameter-values that should be the same across all configured environments. This directory _typically_ contains one or more subdirectories. Subdirectories will one-for-one match with the `common.<NAME>` strings found in the top-level `pillar` directory's `top.sls` file. Each sub-directory will contain one or more `.sls` files that will contain the relevant, common-across-all-environments pillar (per-formula parameter value) data. Thus, if one has a `.../pillar/top.sls` that looks like (as shown in the `top.sls` file subsection):

```yaml
base:
  'G@os_family:RedHat':
    - common.ash-linux
    - common.scap.elx

  'G@os_family:Windows':
    - common.ash-windows
    - common.netbanner
    - common.scap.windows
    - common.winrepo
```

The `.../pillar/common` subdirectory will need to have the subdirectories:

- `ash-linux`
- `ash-windows`
- `netbanner`
- `scap`[^1]
- `winrepo`

Each of the above-listed subdirectories &ndash; with the exception of the `scap` subdirectory will have an `init.sls` file[^2]. Each of these files will contain parameter-dictionaries that align with invoked formulae's `pillar.example` or `pillar.example.yml` files. 

To illustrate behavior tailoring, use the `.../pillar/common/ash-linux/init.sls` file with contents similar to:

```
{%- set os = salt.grains.filter_by({
    'AlmaLinux': 'centos',
    'CentOS': 'centos',
    'CentOS Stream': 'centos',
    'OEL': 'ol',
    'RedHat': 'rhel',
    'Rocky': 'centos',
}, grain='os') %}

ash-linux:
  lookup:
    scap-profile: stig
    scap-cpe: /root/scap/content/openscap/ssg-rhel{{ grains['osmajorrelease'] }}-cpe-dictionary.xml
    scap-xccdf: /root/scap/content/openscap/ssg-{{ os }}{{ grains['osmajorrelease'] }}-xccdf.xml
    scap-ds: /root/scap/content/openscap/ssg-{{ os }}{{ grains['osmajorrelease'] }}-ds.xml
```

Then compare it to the ash-linux project's [pillar.example](https://raw.githubusercontent.com/plus3it/ash-linux-formula/master/pillar.example) file. The project's example file attempts to show available parameters whose values can be set/overridden and how they fit into the parameter-map's structure. In the above, the `ash-linux:lookup:scap-profile` parameter's value is set to `stig`. However, if one consult's the formula-project's `pillar.example` file, it's found that any of the values `stig-rhel7-server-gui-upstream`, `standard`, `pci-dss`, `C2S` or `common` are valid[^3].

As such, if one wanted to make the ash-linux-formula automation use a hardening-profile other than `stig`, one could specify any of the values found in that `pillar.example` file (e.g., change `stig` to `pci-dss` to use the `pci-dss` hardening-profile, instead).

Similarly, if one wanted to change where relevant SCAP-content should be loaded from the `scap-cpe`, `scap-xccdf` and/or `scap-ds` values could all be modified.

### The `<environment>` Directory-Tree(s)

The `<environment>` directory-trees work similarly to the `common` directory tree. The primary difference is focus. Where the `common` directory-tree sets broad-scope behaviors via pillar-variables' parameter/values, the `<environment>` directory-trees set more-limited scopes' behaviors. These directory-trees are intended to align with an infrastructure-as-code environment where an organization has multiple, similar environments that each have specific needs (e.g., to point to per-environment CSP endpoints, security-services servers, etc., install different sets of software or apply different security-benchmarks).

The structure for the `<environment>` directory-trees is much simpler than that for the `common` directory tree. There are no subdirectories under each `<environment>` directory, just a single `init.sls` file. These typically take the form of:

```
{%- load_yaml as os_families %}
RedHat:
  <FORMULA_1_NAME>:
    lookup:
      <var1>: <VALUE>
      <var2>: <VALUE>
      ...
      <varN>: <VALUE>
  ...
  <FORMULA_N_NAME>:
    lookup:
      <var1>: <VALUE>
      <var2>: <VALUE>
      ...
      <varN>: <VALUE>
Windows:
  <FORMULA_1_NAME>:
    lookup:
      <var1>: <VALUE>
      <var2>: <VALUE>
      ...
      <varN>: <VALUE>
  ...
  <FORMULA_N_NAME>:
    lookup:
      <var1>: <VALUE>
      <var2>: <VALUE>
      ...
      <varN>: <VALUE>
```

Each of the `<VALUE>`s listed above may be string, list, dictionary or map data-types. The data-type will be dictated by the needs of the formula and illustrated in the relevant formulae's `pillar.example` or `pillar.example.yml` files. For example, to configure the [mcafee-agent-formula](https://github.com/plus3it/mcafee-agent-formula/) to properly configure Trellix to run on Windows and Linux hosts in the `prod` environment, one would have a `.../pillar/prod/init.sls` file that looked something like:

```
{%- load_yaml as os_families %}
RedHat:
  <FORMULA_1_NAME>:
    lookup:
      <var1>: <VALUE>
      <var2>: <VALUE>
      ...
      <varN>: <VALUE>
  trellix-agent:
    lookup:
      source: s3://enterprise-software/mcafee/mcafee-agent/5.7.9/install.sh
      source_hash: s3://enterprise-software/mcafee/mcafee-agent/5.7.9/install.sh.SHA512
      client_in_ports:
        - 5575
      client_out_ports:
        - 80
        - 443
  ...
  <FORMULA_N_NAME>:
    lookup:
      <var1>: <VALUE>
      <var2>: <VALUE>
      ...
      <varN>: <VALUE>
Windows:
  <FORMULA_1_NAME>:
    lookup:
      <var1>: <VALUE>
      <var2>: <VALUE>
      ...
      <varN>: <VALUE>
  trellix-agent:
    lookup:
      version: '5.7.9.139'
    winrepo:
      versions:
        '5.7.9.139':
          installer: s3://enterprise-software/mcafee/mcafee-agent/5.7.9/FramePkg.exe
  ...
  <FORMULA_N_NAME>:
    lookup:
      <var1>: <VALUE>
      <var2>: <VALUE>
      ...
      <varN>: <VALUE>
```

The above would instruct the mcafee-agent-formula (see the automation's [pillar.example](https://raw.githubusercontent.com/plus3it/mcafee-agent-formula/master/pillar.example) file for insight) automation to:

- Linux: Download and execute the the Trellix 5.7.9 installer from the `s3://enterprise-software/mcafee/mcafee-agent/5.7.9/` bucket-path &ndash; and validate the file's integrity using the checksum file `install.sh.SHA512` from the same S3 bucket-path &ndash; and set up firewalld inbound exceptions for port tcp/5575 and outbound exceptions for ports 80/tcp and 443/tcp.
- Windows: Download and execute the Trellix "Frame" 5.7.9.139 package's executable-installer from the `s3://enterprise-software/mcafee/mcafee-agent/5.7.9/` bucket-path.

Similar `init.sls` content would be needed for any other Watchmaker formula used to install, configure or manage the execution of software.

## The `states` Directory-Tree

This directory-hierarchy governs _which_ Saltstack states will be executed from the available SaltStack formulae. Typically, only modification to this directory's `top.sls` is needed:

- States that are not desired for execution can be commented out or wholly removed.
- States that require conditional-execution can be placed inside of appropriate (Jinja) condition-blocks
- States that are beyond what's defined in the default `top.sls` can be added here to ensure their execution during a full run of watchmaker
- If a change in execution-order is desired, alter the list-order: listed states are executed serially in first-to-last order

## The `winrepo` Directory-Tree

This directory-hierarchy contains windows-specific automation-content. Unlike the `pillar`  and `states` directory-trees, content in this directory-tree is not expected to be multi-platform.

[^1]: In the case of the `scap` directory (and content that functions similarly), instead of an `init.sls` file, it will instead have `.sls` files named to match what's in the `top.sls` file. In the illustrated case, that means a `elx.sls` and a `windows.sls` file.
[^2]: Formulae whose pillar-data is platform-separated such as the `scap` directory's typically will not need an `init.sls` file as the per-platform `.sls` files will directly-referenced and subsume the `init.sls` file's functionality.
[^3]: While efforts are made to keep the examples up to date and correct, it's possible that "valid" parameter-values listed in a given watchmaker-formula project's `pillar.example` file will become invalid over time. If one encounters incorrect or missing exmaple parameter content in a given formula project's `pillar.example` file, please open an issue against that project.
