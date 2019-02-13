.. image:: images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
<br>

# watchmaker

Applied Configuration Management

--------------

## Overview

Watchmaker is intended to help provision a system from its initial installation
to its final configuration. It was inspired by a desire to eliminate static
system images with embedded configuration settings (e.g. gold disks) and the
pain associated with maintaining them.

Watchmaker works as a sort of task runner. It consists of "_managers_" and
"_workers_". A _manager_ implements common methods for multiple platforms
(Linux, Windows, etc). A _worker_ exposes functionality to a user that helps
bootstrap and configure the system. _Managers_ are primarily internal
constructs; _workers_ expose configuration artifacts to users. Watchmaker then
uses a common [configuration file](configuration.html) to determine what
_workers_ to execute on each platform.

## Contents

.. toctree::
    :maxdepth: 1

    installation.md
    configuration.md
    usage.md
    findings/index
    faq.md
    api.md
    contributing.md
    changelog.md

## Supported Operating Systems

*   Enterprise Linux 7 (RHEL/CentOS/etc)
*   Enterprise Linux 6 (RHEL/CentOS/etc)
*   Windows Server 2016
*   Windows Server 2012 R2
*   Windows Server 2008 R2
*   Windows 10
*   Windows 8.1

## Supported Python Versions

*   Python 3.4 and later
*   Python 2.6 and later

NOTE: See relevant [FAQ](faq.html) for details on running ``watchmaker`` in
Python 2.6.
