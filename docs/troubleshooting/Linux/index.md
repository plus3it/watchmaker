```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Linux Log-Files

The logfiles to pay most attention to when running Watchmaker on Enterprise Linux distros (Red Hat, CentOS, Oracle Enterprise, etc.) are as follows:

```{toctree}
:maxdepth: 1
watchmaker.log.md
salt_call.debug.log.md
var-log-messages.md
cloud-init.log.md
cloud-init-output.log.md
```

The above are specifed in the order most-frequently used to determine execution issues.

Note that the troubleshooting discussions assume that `watchmaker` execution has been effected directly through the `cloud-init` service. If `watchmaker` is being executed by other means, the above files may have no relevance to issues encountered running `watchmaker` (the `cloud-init.log` and `cloud-init-output.log`), may not exist in the documented-locations (`salt_call.debug.log` and `watchmaker.log`) and may not even exist at all (`watchmaker.log`).
