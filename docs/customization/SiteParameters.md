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

The `watchmaker` pillar-data is delivered by way of a ZIP-formatted content-archive. While this archive-file typically takes the name `salt-content.zip`, any filename may be used so long as it's properly referenced in the `watchmaker` configuration-file's `salt_content` directive (see the [`config.yaml` discussion](ConfigYaml.md) for a deeper dive into this file's contents, including a discussion of the `salt_content` parameter). The following exmaple configuration-file &ndash; with `salt_content` directive highlighted &ndash; is taken from [watchmaker project](https://github.com/plus3it/watchmaker/blob/main/src/watchmaker/static/config.yaml):

```{eval-rst}
.. literalinclude:: Example-config.yaml
   :emphasize-lines: 10
   :language: yaml
.. note:: If creating a new config-file for customizing your site's ``watchmaker``-execution, it's recommended that config-file content *not* be copied from this document but from the ``watchmaker`` project, directly.
```

As with the configuration-file (passed via the `-c`/`--config` argument to the `watchmaker` utility), this file may be  specified as hosted on the local filesystem, any HTTP/HTTPS URL or an S3-hosted URI.

## Site-Specific Parameters

To implement localized-behavior with watchmaker, it will be necessary to change the `salt_content` paramter's value from `null` to the location of a SaltStack content-bundle. As mentioned previously, the content-bundle should be delivered in the form of a ZIP-formatted content-archive.

The the overall structure and format of the archive-bundle is discussed in the [_Salt Contents Archive File_](SaltContent.md) document. Site-specific _parameters_ &ndash; and associated values &ndash; would be handled within the archive-bundle's [Pillar](SaltContent.md#the-pillar-directory-tree) data contents.

## Bundle locations

Watchmaker currently supports pulling the Saltstack content-bundles from three types of locations: HTTP(S) server, S3 bucket or filesystem-path.  The `salt_content` paramter's value is stated as a URI-notation. See the following subsections for guidance on location-specification.

It's worth noting that Watchmaker has not been tested to (directly) support accessing CIFS- or NFS-based network-shares. If it is desired to access a content-bundle from such a hosting-location, it is recommended to include share-mounting steps in any pre-Watchmaker execution-steps. Once the network-share is mounted, then watchmaker can access the content-bundle as though it was a locally-staged bundle (see below).

### S3-Hosted Bundle

An S3-hosted bundle would be specified like:

```
s3://<BUCKET_NAME>/<FILE_PATH_PREFIX>/<ARCHIVE_FILE_NAME>
```

For example, "`s3://my-site-bukkit/watchmaker/salt-content.zip`"

```{eval-rst}
.. note::
    For S3-hosted URIs, it will be necessary to have ensured that the
    Python Boto3 modules have been installed prior to executing watchmaker
```

### Webserver-Hosted Bundle

A bundle hosted on an HTTP server would be specified like:

```
https://<WEB_SERVER_FQDN>/<FILE_PATH_PREFIX>/<ARCHIVE_FILE_NAME>
```

For example, "`https://wamstuff.my-site.local/watchmaker/salt-content.zip`"

```{eval-rst}
.. note::
    Either HTTP or TLS-encrypted HTTP URIs are supported.

    If potentially-sensitive data will be contained in the site-localization
    archive-file, it is recommended that access to this file be restricted.
    This can typically be done with authorized IP-blocks, API tokens or other
    "simple" authentication credentials. If this limitation comes in the form of
    an API token or a simple-auth credential, it will be necessary to specify
    the token or credentials as part of the HTTP URI.
```

### Locally-staged Bundle

A locally-staged bundle (presumably downloaded and placed as part of a previously-executed launch-time automation-task) would be specified like:

```
file:///<FILESYSTEM_PATH_PREFIX>/<ARCHIVE_FILE_NAME>
```

For example, "`file:///var/tmp/watchmaker/salt-content.zip`"

