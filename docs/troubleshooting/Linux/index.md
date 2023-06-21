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
:maxdepth: 1
watchmaker.log.md
salt_call.debug.log.md
var-log-messages.md
cloud-init.log.md
cloud-init-output.log.md
```

- `/var/log/watchmaker`[^1]
  - `/var/log/watchmaker/salt_call.debug.log`

## `/var/log/watchmaker/salt_call.debug.log`

Where the saltstack content invoked by watchmaker writes its log data to


[^1]: These are the locations when executing watchmaker per the [standard usage guidance](https://watchmaker.readthedocs.io/en/stable/usage.html#linux)
