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

Any automation-formulae that make reference to Pillar data &ndash; typically such formulae will include a `pillar.example` or `pillar.example.yml` in their content-root directory &ndash; may have their behavior modified through content under this directory-tree. Typically, this directory-tree will contain a `common` directory-tree and a directory-tree for each supported deployment environment. Thus, if one is creating behavioral-controls for `dev`, `test` and `prod` environments, the `pillar` directory tree will contain:

- `common`
- `dev`
- `prod`
- `test`

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

### The `<environment>` Directory-Tree(s)

## The `states` Directory-Tree

This directory-hierarchy governs _which_ Saltstack states will be executed from the available SaltStack formulae. Typically, only modification to this directory's `top.sls` is needed:

- States that are not desired for execution can be commented out or wholly removed.
- States that require conditional-execution can be placed inside of appropriate (Jinja) condition-blocks
- States that are beyond what's defined in the default `top.sls` can be added here to ensure their execution during a full run of watchmaker
- If a change in execution-order is desired, alter the list-order: listed states are executed serially in first-to-last order

## The `winrepo` Directory-Tree

This directory-hierarchy contains windows-specific automation-content. Unlike the `pillar`  and `states` directory-trees, content in this directory-tree is not expected to be multi-platform.
