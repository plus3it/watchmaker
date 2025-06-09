```{eval-rst}
.. image:: /images/cropped-plus3it-logo-cmyk.png
    :width: 140px
    :alt: Powered by Plus3 IT Systems
    :align: right
    :target: https://www.plus3it.com
```
<br>

# Findings Summary-Table

A few scans performed against EL9 systems are version-dependent. Watchmaker is designed to ensure that a given EL9 host is running at the latest-available EL9 minor-release version. Some of the version-dependent scans are for versions (well) prior "the latest-available EL9 minor-release version". The person responding to scan-findings should make sure to notice if the findings-text includes mention of specific EL9 minor-release version or version-ranges and compare that to the EL9 minor-release of the scanned system. If the version/version-range is less than that of the scanned version, the scan result may be immediately flagged as "**INVALID FINDING**". Anything that cannot be immediate flagged in this way should be checked against the following table of known findings[^1].


```{eval-rst}
  .. _The OS must be a vendor-supported release: #the-os-must-be-a-vendor-supported-release
  .. _Set the UEFI Boot Loader Password: #set-the-uefi-boot-loader-password
  .. _Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD: #ensure-users-re-authenticate-for-privilege-escalation---sudo-nopasswd
  .. _Support session locking with tmux: #support-session-locking-with-tmux
  .. _Configure tmux to lock session after inactivity: #configure-tmux-to-lock-session-after-inactivity
  .. _Configure the tmux Lock Command: #configure-the-tmux-lock-command
  .. _Only Authorized Local User Accounts Exist on Operating System: #only-authorized-local-user-accounts-exist-on-operating-system
  .. _Set the UEFI Boot Loader Admin Username to a Non-Default Value: #set-the-uefi-boot-loader-admin-username-to-a-non-default-value
  .. _Ensure Logs Sent To Remote Host: #ensure-logs-sent-to-remote-host
  .. _Configure Multiple DNS Servers in /etc/resolv.conf: #configure-multiple-dns-servers-in-/etc/resolv.conf
  .. _The operating system must use a separate file system for /tmp: #rhel-9-must-use-a-separate-file-system-for-/tmp
  .. _Add nodev Option to /tmp: #add-nodev-option-to-/tmp
  .. _Add noexec Option to /tmp: #add-noexec-option-to-/tmp
  .. _Add nosuid Option to /tmp: #add-nosuid-option-to-/tmp
  .. _Configure System to Forward All Mail For The Root Account: #configure-system-to-forward-all-mail-for-the-root-account
  .. _Ensure Chrony is only configured with the server directive: #ensure-chrony-is-only-configured-with-the-server-directive
  .. _Enable SSH Server firewalld Firewall Exception: #enable-ssh-server-firewalld-firewall-exception
  .. _Enable Certmap in SSSD: #enable-certmap-in-sssd
  .. _OS library files must have mode 755 or less permissive: #os-library-files-must-have-mode-755-or-less-permissive

  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | Finding Summary                                                                                                             | Finding Identifiers                              |
  +=============================================================================================================================+==================================================+
  | `The OS must be a vendor-supported release`_                                                                                | V-257777                                         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             | RHEL-09-211010                                   |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Set the UEFI Boot Loader Password`_                                                                                        | content_rule_grub2_uefi_password                 |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD`_                                                    | content_rule_sudo_remove_nopasswd                |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Support session locking with tmux`_                                                                                        | content_rule_configure_bashrc_exec_tmux          |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Configure tmux to lock session after inactivity`_                                                                          | content_rule_configure_tmux_lock_after_time      |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Configure the tmux Lock Command`_                                                                                          | content_rule_configure_tmux_lock_command         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Only Authorized Local User Accounts Exist on Operating System`_                                                            | content_rule_accounts_authorized_local_users     |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Set the UEFI Boot Loader Admin Username to a Non-Default Value`_                                                           | content_rule_grub2_uefi_admin_username           |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Ensure Logs Sent To Remote Host`_                                                                                          | content_rule_rsyslog_remote_loghost              |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Configure Multiple DNS Servers in /etc/resolv.conf`_                                                                       | V-257948                                         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             | RHEL-09-252035                                   |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `The operating system must use a separate file system for /tmp`_                                                            | V-257844                                         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             | RHEL-09-231015                                   |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Add nodev Option to /tmp`_                                                                                                 | V-257866                                         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             | RHEL-09-231125                                   |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Add noexec Option to /tmp`_                                                                                                | V-257867                                         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             | RHEL-09-231130                                   |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Add nosuid Option to /tmp`_                                                                                                | V-257868                                         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             | RHEL-09-231135                                   |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Configure System to Forward All Mail For The Root Account`_                                                                | content_rule_postfix_client_configure_mail_alias |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Ensure Chrony is only configured with the server directive`_                                                               | content_rule_chronyd_server_directive            |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Enable SSH Server firewalld Firewall Exception`_                                                                           | content_rule_firewalld_sshd_port_enabled         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `Enable Certmap in SSSD`_                                                                                                   | content_rule_sssd_enable_certmap                 |
  |                                                                                                                             |                                                  |
  |                                                                                                                             |                                                  |
  +-----------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------+
  | `OS library files must have mode 755 or less permissive`_                                                                   | V-257884                                         |
  |                                                                                                                             |                                                  |
  |                                                                                                                             | RHEL-09-232020                                   |
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

# The OS must be a vendor-supported release

**Conditionally-valid Finding:**

Not Valid Findings:

* During testing (using the `scc` tool), this control was witnessed to misidentify RHEL 9.4 as not being a supported OS release. As of this document's date (2024-06-10), 9.4 is the latest-available release of Red Hat: 9.4 released on 2024-04-30 (see [Red Hat Article #3078](https://access.redhat.com/articles/3078#RHEL9)); 9.5 is due in early November of this year.

Expected Findings:

* CentOS releases never have "vendor support"
* Oracle Linux 9, when used with scanners that implement same evaluation-criteria as the `scc` tool, expect the vendor-string to indicate Red Hat, but the tested file will (rightly) indicate Oracle as vendor

# Set the UEFI Boot Loader Password

**Invalid Finding:**

By default, `watchmaker` will attempt to set a UEFI bootloader password. If the `watchmaker` user does not set the `ash-linux:lookup:grub-passwd` Pillar parameter to a site-custom value, a default value will be used. Currently, this default value is `AR34llyB4dP4ssw*rd`.

```{eval-rst}
.. warning::
    It is `highly` recommended that a site-specific value be set for the
    ``ash-linux:lookup:grub-passwd`` Pillar parameter. While failing to do so will
    not result in a scan-finding, it will mean that anyone that has read this
    document -- or who has reviewed the watchmaker source-code -- will know your
    servers' bootloader password
```

# Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD

**Conditionally-valid Finding:**

Accounts configured for token- or key-based logins typically do not have passwors set. This is common on systems that leverage the [`cloud-init` service](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_and_managing_cloud-init_for_rhel_9/index) to configure a default- or provisioning-user account. Similary, PIV-enabled accounts will typically not have passwords.

On AWS-hosted systems, the default-/provisioning user is configured with no password set, instead relying on SSH key-based logins for authentication. For such user-accounts, in order to provide the ability to use `sudo`, the `NOPASSWD` option must be set.

The watchmaker automation normally comments out any `sudoers` entries that may be defined. However, to preserve expected functionality for the `cloud-init`-created default-/provisioning-user, removal of the `NOPASSWD` directive is _not_ performed against the `/etc/sudoers.d/90-cloud-init-users` file. Therefore, this finding is expected on systems that leverage the `cloud-init` service to configure a default- or provisioning-user account. Systems that do not leverage the `cloud-init` service to configure a default- or provisioning-user account should have no findings of this type listed.

# Support session locking with tmux

**Invalid Finding:**

Watchmaker addresses this security-control. However, many scanners' check-automation have inflexible pattern-matching which are unable to properly detect that the finding _has_ been addressed

# Configure tmux to lock session after inactivity

**Invalid Finding:**

The configuration-automation within `watchmaker` will configure the `tmux` service per the STIGs. If this finding pops up, it will be necessary to ensure that:

* The associated `watchmaker` state (`.../el9/RuleById/medium/content_rule_configure_tmux_lock_after_time`) actually ran _and_ ran to successful completion
* The `watchmaker`-set value is the same as the site's prescribed-value

# Configure the tmux Lock Command

**Invalid Finding:**

The configuration-automation within `watchmaker` will configure the `tmux` service per the STIGs. If this finding pops up, it will be necessary to ensure that:

* The associated `watchmaker` state (`.../el9/RuleById/medium/content_rule_configure_tmux_lock_command`) actually ran _and_ ran to successful completion
* The `watchmaker`-set value is the same as the site's prescribed-value

# Only Authorized Local User Accounts Exist on Operating System

**Expected Finding:**

"Authorized Local User Accounts" is a wholly site-specific determination. As some scanners note in their report-output:

```
Automatic remediation of this control is not available due to the unique requirements of each system
```

As a result, most scanners will emit this in their findings-reports as an indication to the assessor that a manual check of the system's local users conform to site-local policies

# Set the UEFI Boot Loader Admin Username to a Non-Default Value

**Invalid Finding:**

By default, `watchmaker` will attempt to set a custom superuser name for the UEFI bootloader. If the `watchmaker` user does not set the `ash-linux:lookup:grub-user` Pillar parameter to a site-custom value, a default value will be used. Currently, this default value is `grubuser`.

```{eval-rst}
.. warning::
    It is `highly` recommended that a site-specific value be set for the
    ``ash-linux:lookup:grub-user`` Pillar parameter. While failing to do so will
    not result in a scan-finding, it will mean that anyone that has read this
    document will know your servers' bootloader superuser name
```

# Ensure Logs Sent To Remote Host

**Expected Finding:**

"Ensure Logs Sent To Remote Host" is a wholly site-specific determination. While most scanners will look for whether log-offloading via `rsyslog` has been set up, this scan-criteria is generally not valid:

* Many sites use tools _other than_ `rsyslog` to handle log-offloading (Splunk, FluentBit, CSP-specific log-agents have all been used by various organizations that use watchmaker to harden their systems
* Even sites that _do_ use `rsyslog` to handle log-offloading, the scanners frequently look only for the log-destination `logcollector` - or similarly-generic destination-name - rather than the hostname, FQDN or IP address of the log-collection server

It will be up to the system assessor to know the site-specific implementation-requirements and validate accordingly

# The operating system must use a separate file system for /tmp

**Invalid Finding:**

If the scan-target implements the `/tmp` filesystem as a (`tmpfs`) pseudofileystem, some scanners will fail to properly detect that the STIG-specified standalone mount has been configured.

# Add nodev Option to /tmp

**Invalid Finding:**

If the scan-target implements the `/tmp` filesystem as a (`tmpfs`) pseudofileystem &ndash; or otherwise implements the `/tmp` filesystem's mount-options by way of a systemd options file &ndash; some scanners will fail to properly detect that the STIG-specified mount-options have been configured.

# Add noexec Option to /tmp

**Invalid Finding:**

If the scan-target implements the `/tmp` filesystem as a (`tmpfs`) pseudofileystem &ndash; or otherwise implements the `/tmp` filesystem's mount-options by way of a systemd options file &ndash; some scanners will fail to properly detect that the STIG-specified mount-options have been configured.

# Add nosuid Option to /tmp

**Invalid Finding:**

If the scan-target implements the `/tmp` filesystem as a (`tmpfs`) pseudofileystem &ndash; or otherwise implements the `/tmp` filesystem's mount-options by way of a systemd options file &ndash; some scanners will fail to properly detect that the STIG-specified mount-options have been configured.

# Configure Multiple DNS Servers in /etc/resolv.conf

**Expected Finding:**

In many environments, particularly CSP hosting-environments, "individual" DNS servers are actually highly-available services that answer at a single, highly-available IP address. As such, configuaration of multiple DNS servers may not only not be possible but may actually cause functionality-breaking problems.

# Configure System to Forward All Mail For The Root Account

**Conditionally-valid Finding:**

Forwarding-rules for a system's `root` user account is a wholly enterprise-specific &ndash; or even specific to service-group or individual-system level &ndash; determination. While watchmaker _can_ be used to close this finding (via the `.../el9/RuleById/medium/content_rule_postfix_client_configure_mail_alias` control/handler), it relies on the `ash-linux:lookup:root-mail-dest` Pillar-parameter having a value set. If this value is _not_ set, then watchmaker will not close this finding.

```{eval-rst}
.. note::
    ``watchmaker``'s automation-content does not have the capability of ensuring that:

    * The Pillar-parameter's ``ash-linux:lookup:root-mail-dest`` value is set to a valid email destination
    * Even if the ``ash-linux:lookup:root-mail-dest`` value `is` set to a valid email destination, forwarding to that destination will actually `function`

```

# Ensure Chrony is only configured with the server directive

**Conditionally-valid Finding:**

Setup of the `chrony` time-synchronization system can be very site-specific. In fact, some sites may choose not to set it up, at all, due to having other methods for ensuring that their hosts' time is kept properly-synchronized with an authoritative source. By default, `watchmaker` will make no changes to the configuration of the `chrony` time-synchronization service unless one sets the `ash-linux:lookup:use-ntp` Pillar parameter to `True`. If set to `True`, `watchmaker` will attempt to close this finding:

* If one further defines the `ash-linux:lookup:ntp-servers` Pillar-parameter to a list of NTP servers, `watchmaker` will close the finding by configuring the `chrony` service to use that list of servers
* If one fails to define the `ash-linux:lookup:ntp-servers` Pillar-parameter `watchmaker` will close the finding by configuring the `chrony` service to a default list of servers (the per-vendor "pool" NTP servers maintained by the [Network Time Protocol (NTP) Project](https://ntp.org))

# Enable SSH Server firewalld Firewall Exception

**Invalid Finding:**

This finding may be triggered if only the `ssh` _ports_ are scanned for. The `watchmaker` hardening routines ensure that a broad-scoped (i.e., "allow from all") firewalld exception is made for the `ssh` _service_. The implementation-difference may be seen by comparing the outputs of `firewall-cmd --list-services`

```
# firewall-cmd --list-services | sed 's/\s\s*/\n/g' | grep ssh
ssh
```

and `firewall-cmd --list-ports`:

```
# firewall-cmd --list-ports | grep ^22
22/tcp
```

Watchmaker's implementation will show up only in the output of the former. Some scanners may only expect the exception to show up in the latter.

# Enable Certmap in SSSD

**Expected Finding:**

Because configuration of the `sssd` service to perform SmartCard-based authentication is an inherently-local configuration-task (and because no suitable testing environment has been provided to this project-team to prototype against), `watchmaker` makes no attempt to configure `sssd` service to perform SmartCard-based authentication.

# OS library files must have mode 755 or less permissive

**Conditionally-valid Finding:**

Scanners should typically only search in the directories `/lib`, `/lib64`, `/usr/lib` and `/usr/lib64` for this finding. Overly-broad scans of those directories _may_ turn up the files:

* `/lib/polkit-1/polkit-agent-helper-1`
* `/usr/lib/polkit-1/polkit-agent-helper-1`

```{eval-rst}
.. note::
    The ``/lib/polkit-1/polkit-agent-helper-1`` will be a symbolic-link pointing
    to ``/usr/lib/polkit-1/polkit-agent-helper-1``
```

These are files that _need_ to set to mode `4755` &ndash; permissions that are broader than the mode `0755` permitted under this finding.

```{eval-rst}
.. warning::
    Changing these files' permissions to make them no longer show up on scans
    `will` break the hardened system.
```

Any files other than `/lib/polkit-1/polkit-agent-helper-1` and `/usr/lib/polkit-1/polkit-agent-helper-1` should be treated as valid findings and remediated.


[^1]: Do not try to perform an exact-match from the scan-report to this table. The findings table's link-titles are distillations of the scan-findings title-text rather than being verbatim copies.
