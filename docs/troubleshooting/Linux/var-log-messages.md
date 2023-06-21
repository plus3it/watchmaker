```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# The `/var/log/messages` Log-File

This is Red Hat Enterprise Linux's default/primary logging location for miscellaneous system activities. Any init- or systemd-launched service that emits output to STDERR or STDOUT will typically (also) log to this file.[^1]

Typically, the provisioning-administrator will wish to review this file to trace where failures in the invocation of watchmaker have failed or where errors in an instance's/VM's userData payload has encountered errors.

- Search, case-insensitively, for the string "`watchmaker`" to find logged-content explicit to the execution of watchmaker. Depending how far watchmaker got before failing, there can be a significant amount of output to pore through (recommend piping to a pagination-tool such as `less`)
- Search for the string "`\ cloud-init:\ `" to find logged-content related to the `cloud-init` service. This search-string will reveal execution-output made to STDOUT and STDERR by any processes initiated by the `cloud-init` service. This will _typically_ include watchmaker and any logging-enabled userData script-output. Search output will tend to be even more-significant than looking just for `watchmaker` (therefore, also recommend piping to a pagination-tool such as `less`)

The use of the qualifier, "typically", in the prior bullet is required to account for different methods for invoking `watchmaker`. Some `watchmaker`-users leverage methods such as CloudFormation and other templating-engines, Ansible and other externalized provisioning-services, etc. to launch the `watchmaker` process. Those methods are outside the scope of this document. The relevant logging should be known to the user of these alternate execution-frameworks.


[^1]: Some sites will explicitly disable local logging to this file. If this has been done, data that normally shows up in `/var/log/messages` _may_, instead, be found in the systemd output logs. See the [Using journald](journald.rst) document for a fuller detailing of using `journald` logging.
