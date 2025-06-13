```{eval-rst}
.. image:: /images/cropped-plus3it-logo-cmyk.png
    :width: 140px
    :alt: Powered by Plus3 IT Systems
    :align: right
    :target: https://www.plus3it.com
```
<br>

# CentOS Stream Discontinuation Notes

With the CentOS maintainers having discontinued CentOS Stream 8 at the end of
May of 2024, access to security-update and feature content is no longer
available within the repositories activated by default in templates and systems
deployed prior to that date. As a result, hardening-operations that require the
installation of either additional packages or updates to already-installed
packages will fail. This may be worked around by deactivating the standard
repositories and creating "vault" repositories from them. This may be done with
a quick script like:

```
# (
  cd /etc/yum.repos.d &&
  for RepoFile in CentOS-Stream-{BaseOS,AppStream,Extras{,-common},HighAvailability,NFV,PowerTools,RealTime,ResilientStorage}.repo
  do
    sed -e '/^mirrorlist/s/^/##/' \
        -e '/baseurl=/s/^#*//' \
        -e '/baseurl=/s/mirror\.centos\.org/vault.centos.org/' \
        -e '/\[/s/^\[/&vault-/' \
        -e '/^name/s/$/ (Vault)/' \
      "${RepoFile}" > "${RepoFile//.repo/-Vault.repo}"
  done
)
# dnf config-manager --save --set-disabled appstream baseos extras
# dnf config-manager --save --set-enabled vault-{appstream,baseos,extras}
```
