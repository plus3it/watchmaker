```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# The `/var/log/watchmaker/watchmaker.log` Log-File

This file tracks the top-level execution of the `watchmaker` configuration-utility. This file should always exist, unless:

- The provisioning-administrator has checked before the utility has been downloaded and an execution-attempted. This typically happens if a `watchmaker`-execution is attempted late in a complex provisioning-process
- An execution-attempt wholly failed. In this case, check the logs for the `watchmaker`-calling service or process (e.g. [`cloud-init`](cloud-init.log.md))
- The provisioning-administrator has not invoked `watchmaker` in accordance with the `watchmaker` project's usage-guidance: if a different logging-location was specified (e.g., by adding a flag/argument like `--log-dir=/tmp/watchmaker`), the provisioning-administrator would need to check the alternately-specified logging-location.
- The provisioning-administrator invoked the `watchmaker`-managed _content_ directly (e.g., using `salt-call -c /srv/watchmaker/salt`). In this scenario, only the content-execution may have been logged (whether logging was captured and where would depend on how the direct-execution was requested).

## Typical Errors

* Bad specification of configuration file. This will typically come with an HTTP 404 error similar to:
    ~~~
    botocore.exceptions.ClientError: An error occurred (404) when calling the HeadObject operation: Not Found
    ~~~
* Attempt to use a protected configuration-file. This will typically come win an HTTP 403 error. Most typically, this happens when the requested configuration-file exists on a protected network share and the requesting-process doesn't have permission to access it.
