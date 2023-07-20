```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# The `c:\watchmaker\logs\watchmaker.log` Log-File

This file tracks the top-level execution of the watchmaker configuration-utility. This file should _always_ exist. The primary reasons that it may not exist are:

- The provisioning-administrator has checked for the log before the ``watchmaker``-utility has been downloaded and an execution-attempted. This typically happens if a ``watchmaker``-execution is attempted late in a complex provisioning-process

- An execution-attempt wholly failed. In this case, check the logs for the watchmaker-calling service or process.

- The provisioning-administrator has not invoked ``watchmaker`` in accordance with the ``watchmaker`` project's usage-guidance: if a different logging-location was specified (e.g., by adding a flag/argument like ``--log-dir=C:\TEMP\watchmaker``), the provisioning-administrator would need to check the alternately-specified logging-location.

- The provisioning-administrator invoked the ``watchmaker``-managed content directly (e.g., using ``salt-call -c c:\watchmaker\salt\conf state.highstate``). In this scenario, only the content-execution may have been logged (whether logging was captured and where would depend on how the direct-execution was requested).

## Location Note

The cited-location of the main ``watchmaker``-execution's log-file is predicated on the assumption that ``watchmaker`` has been executed per the Usage-guidance for [Windows](../../usage.md#windows):

```{eval-rst}
.. literalinclude:: ../../usage.d/userData-Windows.ps1
   :language: shell
   :emphasize-lines: 21
```

The value of the ``--log-dir`` parameter sets the directory-location where ``watchmaker`` will create its log-files, including the ``watchmaker.log`` file. If a different value is set for the ``--log-dir`` parameter, the log-file will be created in _that_ directory-location, instead.


## Typical Errors

* Bad specification of remotely-hosted configuration file. This will typically come with an HTTP 404 error similar to:
    ~~~
    botocore.exceptions.ClientError: An error occurred (404) when calling the HeadObject operation: Not Found
    ~~~
    Ensure that the requested URI for the remotely-hosted configuration file is valid.
* Attempt to use a protected, remotely-hosted configuration-file. This will typically come win an HTTP 403 error. Most typically, this happens when the requested configuration-file exists on a protected network share and the requesting-process doesn't have permission to access it.
    ~~~
    botocore.exceptions.ClientError: An error occurred (403) when calling the HeadObject operation: Forbidden
    ~~~
    Ensure that `watchmaker` has adequate permissions to access the requested, remotely-hosted configuration file.
* Remotely-hosted configuration file is specified as an `s3://` URI without installation of `boto3` Python module. This will typically come with an error similar to:
    ```{eval-rst}
    .. literalinclude:: ../NoBoto3-LogSnippet.txt
       :language: text
       :emphasize-lines: 1-2
    ```
    Ensure that the `boto3` Python module has been installed _prior to_ attempting to execute `watchmaker`

## Alternate Logs

As noted above, this logfile may not exist if execution of watchmaker has wholly failed. If the execution was attempted via automated-startup methods but there is no watchmaker logfile, it will be necessary to check the CSP provider-logs. On AWS, the logs to check (per the [vendor documentation](https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/ec2-windows-user-data.html#user-data-execution)) will be:

* If using (legacy) EC2Launch, the log-file to search will be [``C:\ProgramData\Amazon\EC2-Windows\Launch\Log\UserdataExecution.log``](c_amazon_EC2Launch_Log_UserdataExecution.log.md)
* If using EC2Launch v2, the log-file to search will be [``C:\ProgramData\Amazon\EC2Launch\log\agent.log``](c_amazon_EC2Launch_v2_Log_UserdataExecution.log.md)
