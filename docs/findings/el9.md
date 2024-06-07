```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Findings Summary-Table

A few scans performed against EL9 systems are version-dependent. Watchmaker is designed to ensure that a given EL9 host is running at the latest-available EL9 minor-release version. Some of the version-dependent scans are for versions (well) prior "the latest-available EL9 minor-release version". The person responding to scan-findings should make sure to notice if the findings-text includes mention of specific EL9 minor-release version or version-ranges and compare that to the EL9 minor-release of the scanned system. If the version/version-range is less than that of the scanned version, the scan result may be immediately flagged as "**INVALID FINDING**". Anything that cannot be immediate flagged in this way should be checked against the following table of known findings[^1].


```{eval-rst}
  .. _Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD: #ensure-users-re-authenticate-for-privilege-escalation---sudo-nopasswd
  .. _Support session locking with tmux: #support-session-locking-with-tmux
  .. _Only Authorized Local User Accounts Exist on Operating System: #only-authorized-local-user-accounts-exist-on-operating-system
  .. _Ensure Logs Sent To Remote Host: #ensure-logs-sent-to-remote-host
  .. _Configure Multiple DNS Servers in /etc/resolv.conf: #configure-multiple-dns-servers-in-/etc/resolv.conf
  .. _Configure System to Forward All Mail For The Root Account: #configure-system-to-forward-all-mail-for-the-root-account


  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | Finding Summary                                                                                                             | Finding Identifiers                              |
  +=============================================================================================================================+==================================================+
  | `Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD`_                                                    | content_rule_sudo_remove_nopasswd                |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Support session locking with tmux`_                                                                                        | content_rule_configure_bashrc_exec_tmux          |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Only Authorized Local User Accounts Exist on Operating System`_                                                            | content_rule_accounts_authorized_local_users     |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Ensure Logs Sent To Remote Host`_                                                                                          | content_rule_rsyslog_remote_loghost              |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Configure Multiple DNS Servers in /etc/resolv.conf`_                                                                       | content_rule_network_configure_name_resolution   |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Configure System to Forward All Mail For The Root Account`_                                                                | content_rule_postfix_client_configure_mail_alias |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
```

```{eval-rst}
.. note::
   This document is being written early in the adoption-cycle for DISA-mandated
   security-controls. As such, some of the automation and associated scan-finding
   are for pre-release content. Such content will typically lack the
   finding-identifiers within the DISA content (e.g., the vulnerability IDs that
   take a format like ``V-<SIX_DIGIT_STRING>`` and vendor IDs that take the
   format ``<OSID>-08-<FINDING_ID>``)
```

# Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD

**Condtionally-valid Finding:**

On systems that leverage the [`cloud-init` service](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_and_managing_cloud-init_for_rhel_9/index) to configure a default- or provisioning-user account. In turn, that account is typically configured to _only_ allow key-based logins to those accounts. As a result, those accounts do not have passwords set (their `/etc/shadow` file's password-hash field-entries are set to `!!`). The `cloud-init` service enables `sudoer` capabilities through entries it creates in the `/etc/sudoers.d/90-cloud-init-users` file.

The watchmaker automation normally comments out any `sudoers` entries that may be defined. However, to preserve expected functionality for the `cloud-init`-created default-/provisioning-user, removal of the `NOPASSWD` directive is _not_ performed against the `/etc/sudoers.d/90-cloud-init-users` file. Therefore, this finding is expected on systems that leverage the `cloud-init` service to configure a default- or provisioning-user account (primarily AWS-hosted EC2s). Systems that do not leverage the `cloud-init` service to configure a default- or provisioning-user account should have no findings of this type listed.

# Support session locking with tmux

**Invalid Finding:**

Watchmaker addresses this security-control. However, many scanners' check-automation have inflexible pattern-matching which are unable to properly detect that the finding _has_ been addressed

# Only Authorized Local User Accounts Exist on Operating System

**Expected Finding:**

"Authorized Local User Accounts" is a wholly site-specific determination. As some scanners note in their report-output:

```
Automatic remediation of this control is not available due to the unique requirements of each system
```

As a result, most scanners will emit this in their findings-reports as an indication to the accreditor that a manual check of the system's local users conform to site-local policies

# Ensure Logs Sent To Remote Host

**Expected Finding:**

"Ensure Logs Sent To Remote Host" is a wholly site-specific determination. While most scanners will look for whether log-offloading via `rsyslog` has been set up, this scan-criteria is generally not valid:

* Many sites use tools _other than_ `rsyslog` to handle log-offloading (Splunk, FluentBit, CSP-specific log-agents have all been used by various organizations that use watchmaker to harden their systems
* Even sites that _do_ use `rsyslog` to handle log-offloading, the scanners frequently look only for the log-destination `logcollector` - or similarly-generic destination-name - rather than the hostname, FQDN or IP address of the log-collection server

It will be up to the system accreditor to know the site-specific implementation-requirements and validate accordingly

# Configure Multiple DNS Servers in /etc/resolv.conf

**Expected Finding:**

In many environments, particularly CSP hosting-environments, "individual" DNS servers are actually highly-available services that answer at a single, highly-available IP address. As such, configuaration of multiple DNS servers may not only not be possible but may actually cause functionality-breaking problems.

# Configure System to Forward All Mail For The Root Account

**Condtionally-valid Finding:**

Forwarding-rules for a system's `root` user account is a wholly enterprise-specific &ndash; or even specific to service-group or individual-system level &ndash; determination. While watchmaker _can_ be used to close this finding (via the `.../el9/RuleById/medium/content_rule_postfix_client_configure_mail_alias` control/handler), it relies on the `ash-linux:lookup:root-mail-dest` Pillar-parameter having a value set. If this value is _not_ set, then watchmaker will not close this finding.

```{eval-rst}
.. note::
   ``watchmaker``'s automation-content does not have the capability of ensuring that:

   * The Pillar-parameter's ``ash-linux:lookup:root-mail-dest`` value is set to a valid email destination
   * Even if the ``ash-linux:lookup:root-mail-dest`` value `is` set to a valid email destination, forwarding to that destination will actually `function`

```



[^1]: Do not try to perform an exact-match from the scan-report to this table. The findings table's link-titles are distillations of the scan-findings title-text rather than being verbatim copies.
