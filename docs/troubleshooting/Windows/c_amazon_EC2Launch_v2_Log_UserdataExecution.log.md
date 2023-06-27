```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# The `C:\ProgramData\Amazon\EC2Launch\log\agent.log` Log-File

```{eval-rst}
.. warning:: Watchmaker has not yet been tested with the EC2Launch v2 service. As of the writing of this document, the recommended userData content does not function under EC2Launch v2. This document is *very* beta, and primarily acts as a place-holder.
```

This file tracks the top-level execution of any tasks specified in a Windows Server EC2's userData payload. This file should _always_ exist. The primary reasons that it may not exist are:

- The EC2 was launched from an AMI that leverages the (legacy) ``EC2Launch`` method
- The EC2 was launched from an AMI that does not have the tooling to support parsing/executing a userData

Windows AMIs published through the Amazon/Microsoft partnership will always contain the tooling to support either the ``EC2Launch`` or ``EC2Launch v2`` parsing/execution of userData payloads:
- Windows Server 2022 and higher AMIs use the ``EC2Launch v2`` userData payload-handler
- Windows Server 2012, 2016 and 2019 AMIs use the ``EC2Launch`` userData payload-handler unless their AMI-names start with the string "``EC2LaunchV2-``"

To get a list of Windows 2012, 2016 or 2019  AMIs that leverage the ``EC2Launch v2`` userData payload-handler, use a (CLI) query similar to:

```
aws ec2 describe-images \
  --owner amazon \
  --filters 'Name=name,Values=EC2LaunchV2-Windows_Server-201*' \
  --query 'Images[].[CreationDate,ImageId,Name]' \
  --output text
```

