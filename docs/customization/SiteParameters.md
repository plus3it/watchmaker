```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Modifying Formulae Execution-Parameters

The `watchmaker` utility bundles several SaltStack formulae. These bundled-formulae's behaviors are, in turn, governed, by a set of [Pillar](https://docs.saltproject.io/en/getstarted/config/pillar.html)-data that are also bundled with the `watchmaker`utility: pillar-data is how SaltStack states' behaviors may be modified. Sites that wish to either override the bundled-formulae's default behaviors or wish to run additional SaltStack formulae that are _not_ in the default formula-bundle &ndash; and need to provide supporting behvior-tailoring &ndash; can do so by creating custom pillar-data.

## Reference

When customizing Pillar content, it will also be necessary to use a site-specific, YAML-formatted configuration-file. Per the "[Usage](../usage.md)" document's "from the CLI" section, this file is _typically_ named `config.yaml`. Any file name can be used so long as it matches what is passed via the `-c`/`--config` argument to the `watchmaker` utility. Further, this configuration-file may be specified as hosted on the local filesystem, any HTTP/HTTPS URL or an S3-hosted URI.

The `watchmaker` pillar-data is delivered by way of a ZIP-formatted content-archive. While this archive-file typically takes the name `salt-content.zip`, any filename may be used so long as it's properly refer in the `watchmaker` configuration-file's `salt_content` directive. The following exmaple configuration-file &ndash; with `salt_content` directive highlighted &ndash; is taken from [watchmaker project](https://github.com/plus3it/watchmaker/blob/main/src/watchmaker/static/config.yaml):

```{eval-rst}
.. literalinclude:: Example-config.yaml
   :emphasize-lines: 10
   :language: yaml
.. note:: If creating a new config-file for customizing your site's ``watchmaker``-execution, it's recommended that config-file content _not_ be copied from this document but from the ``watchmaker`` project, directly.
```

As with the configuration-file (passed via the `-c`/`--config` argument to the `watchmaker` utility), this file may be  specified as hosted on the local filesystem, any HTTP/HTTPS URL or an S3-hosted URI.

