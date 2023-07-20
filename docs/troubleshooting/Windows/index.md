```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Windows Log-Files

When using `watchmaker` on Windows servers, the primary log-files of interest are:

```{toctree}
:maxdepth: 1
c_watchmaker_logs_watchmaker.log.md
c_watchmaker_logs_salt_call.debug.md

There can be other files in the `c:\watchmaker\logs\` directory, but the ones present will depend on what enterprise-integration features have been selected for `watchmaker` to attempt to execute and whether those integrations are configured to log independently.

There may be further log-files of interest, depending on how much execution-progress `watchmaker` has made and how `watchmaker` has been invoked.

## AWS:

- [`C:\ProgramData\Amazon\EC2Launch\log\agent.log`](c_amazon_EC2Launch_Log_UserdataExecution.log.md)
- [`C:\ProgramData\Amazon\EC2-Windows\Launch\Log\UserdataExecution.log`](c_amazon_EC2Launch_v2_Log_UserdataExecution.log.md)


```{toctree}
:maxdepth: 1
:hidden:
c_watchmaker_logs_watchmaker.log.md
c_watchmaker_logs_salt_call.debug.md
c_amazon_EC2Launch_Log_UserdataExecution.log.md
c_amazon_EC2Launch_v2_Log_UserdataExecution.log.md
```
