```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Linux Log-Files

The logfiles to most-frequently pay attention to when running Watchmaker on Enterprise Linux distros (Red Hat, CentOS, Oracle Enterprise, etc.) are as follows:

```{toctree}
:maxdepth: 0
watchmaker.log.md
salt_call.debug.log.md
var-log-messages.md
cloud-init.log.md
cloud-init-output.log.md
```

- `/var/log/cloud-init.log`
- `/var/log/cloud-init-output.log`[^1]
- `/var/log/watchmaker`[^2]
  - `/var/log/watchmaker/watchmaker.log`
  - `/var/log/watchmaker/salt_call.debug.log`

## `/var/log/cloud-init.log`

Default location where the Red Hat packaged version of the `cloud-init`[^3] service for Enterprise Linux 6 and 7 writes all of its log-output to. On RHEL 8+, logging data is split-out across this file and the `/var/log/cloud-init-output.log` file

## `/var/log/cloud-init-output.log`

Default location where the Red Hat packaged version of the `cloud-init` service for Enterprise Linux 8 and higher writes its summary log-output to.

## `/var/log/watchmaker/watchmaker.log`

Where the watchmaker service writes its log-data to.

## `/var/log/watchmaker/salt_call.debug.log`

Where the saltstack content invoked by watchmaker writes its log data to


[^1]: Red Hat 8 and newer (and clones) have a newer version of cloud-init than was available on Red Hat 7 and lower. The new version has additional default logging-locations defined
[^2]: These are the locations when executing watchmaker per the [standard usage guidance](https://watchmaker.readthedocs.io/en/stable/usage.html#linux)
[^3]: On Linux systems, `cloud-init` is the standard method for executing [userData content](https://cloudbase-init.readthedocs.io/en/latest/userdata.html).
[^4}: If local logging has been disconfigured, data that normally shows up in `/var/log/messages` _may_ also be visible in the systemd output logs
