```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# The `c:\watchmaker\logs\salt_call.debug` Log-File

This file captures the execution-activities of [SaltStack](https://docs.saltproject.io/en/latest/contents.html) formulae. This file will exist if `watchmaker` has be able to successfully download and install its (SaltStack-based) configuration-content. 

The primary diagnostic interest in this file is if there is an execution-failure within a managed-content module. By default, `watchmaker` will reboot a system after a successful run[^1]. If the expected reboot occurs, this file likely will not be of interest. If the reboot fails to occur and the `watchmaker` log indicates that it was able to start the SaltStack-based operations, then consult this file to identify what failed and (possibly) why.

## Typical Errors

Any errors encountered by SaltStack will typically have a corresponding log-section that starts with a string like:

```
2023-06-27 12:57:39,841 [salt.state       :325 ][ERROR   ][5656] { ... }
```

Errors from the failing SaltStack action will typically include an embedded JSON-stream. The above snippet's `{ ... }` stands in for an embedded JSON-stream (for brevity's sake). Depending how long the embedded JSON-stream is, it will probably make things easier for the provisioning-user to convert that stream to a more human-readable JSON document-block.

The most commonly-reported issues are around:

- Domain Join Errors

### Domain Join Error

Errors in joining the host to active directory can have several causes. The three most typical are:

- Bad join-user credentials (or locked-out account)
- Inability to find domain controllers
- Inability to communicate with found domain controllers.

The following is version of the salt_call.debug log file with a join-domain failure. The version shown has the JSON-stream expanded into a (more-readable) JSON-document. The original content can [be viewed](salt.debug.join-fail-stream.txt) to illustrate _why_ expanding the JSON-stream makes the provisioning-administrator's life easier.


```{eval-rst}
.. literalinclude:: salt.debug.join-fail-expanded.txt
   :language: text
   :emphasize-lines: 228-232,253-257,278-282
```




[^1]: This behavior may be overridden by having invoked `watchmaker` with the `-n` flag
