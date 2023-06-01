```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Findings Summary-Table

```{eval-rst}
  .. _Use Only FIPS 140-2 Validated Ciphers: #use-only-fips-140-2-validated-ciphers
  .. _Use Only FIPS 140-2 Validated MACs: #use-only-fips-140-2-validated-macs
  .. _Modify the System Login Banner: #modify-the-system-login-banner
  .. _Enable Smart Card Login: #enable-smart-card-login
  .. _Configure the Firewalld Ports: #configure-the-firewalld-ports
  .. _Set Default firewalld Zone for Incoming Packets: #set-default-firewalld-zone-for-incoming-packets
  .. _Disable Kernel Parameter for IP Forwarding: #disable-kernel-parameter-for-ip-forwarding
  .. _The Installed Operating System Is Vendor Supported: #the-installed-operating-system-is-vendor-supported
  .. _Install McAfee Virus Scanning Software: #install-mcafee-virus-scanning-software
  .. _Enable FIPS Mode in GRUB2: #enable-fips-mode-in-grub2
  .. _Configure AIDE to Use FIPS 140-2 for Validating Hashes: #configure-aide-to-use-fips-140-2-for-validating-hashes
  .. _Verify and Correct Ownership with RPM: #verify-and-correct-ownership-with-rpm
  .. _Verify and Correct File Permissions with RPM: #verify-and-correct-file-permissions-with-rpm
  .. _Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD: #ensure-users-re-authenticate-for-privilege-escalation---sudo-nopasswd
  .. _Operating system must display the date and time of the last successful account login upon logon: #operating-system-must-display-the-date-and-time-of-the-last-successful-account-logon-upon-logon
  .. _Operating system must be configured so that the audit system takes appropriate action when the audit storage volume is full: #operating-system-must-be-configured-so-that-the-audit-system-takes-appropriate-action-when-the-audit-storage-volume-is-full
  .. _Operating system must be configured to off-load audit logs onto a different system or storage media from the system being audited: #operating-system-must-be-configured-to-off-load-audit-logs-onto-a-different-system-or-storage-media-from-the-system-being-audited
  .. _User Must Not Be Allowed To Change Password More-frequently than once per 24 hours: #user-must-not-be-allowed-to-change-password-more-frequently-than-once-per-24-hours
  .. _User Must Change Password At Least Once Every Sixty Days: #user-must-change-password-at-least-once-every-sixty-days
  .. _User Must Be Provided Adequate Warning Of Password-Expiration: #user-must-be-provided-adequate-warning-of-password-expiration
  .. _User Account Must Be Expired N Days After Password Has Expired: #user-account-must-be-expired-n-days-after-password-has-expired
  .. _For Operating Systems Using DNS Resolution, At Least Two Name Servers Must Be Configured: #for-operating-systems-using-dns-resolution,-at-least-two-name-servers-must-be-configured
  .. _The OS Must Elevate The SELinux Context When An Administrator Calls The Sudo Command: #the-os-must-elevate-the-selinux-context-when-an-administrator-calls-the-sudo-command




  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | Finding Summary                                                                                                                      | Finding Identifiers |
  +======================================================================================================================================+=====================+
  | `Use Only FIPS 140-2 Validated Ciphers`_                                                                                             | SV-86845            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-040110      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Use Only FIPS 140-2 Validated MACs`_                                                                                                | SV-86877            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-040400      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Modify the System Login Banner`_                                                                                                    | SV-86487            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-010050      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Enable Smart Card Login`_                                                                                                           | SV-86589            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-010500      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Configure the Firewalld Ports`_                                                                                                     | SV-86843            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-040100      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Set Default firewalld Zone for Incoming Packets`_                                                                                   | SV-86939            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-040810      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Disable Kernel Parameter for IP Forwarding`_                                                                                        | SV-86933            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-040740      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `The Installed Operating System Is Vendor Supported`_                                                                                | SV-86621            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-020250      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Install McAfee Virus Scanning Software`_                                                                                            | SV-86837            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-032000      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Enable FIPS Mode in GRUB2`_                                                                                                         | SV-86691            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-021350      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Configure AIDE to Use FIPS 140-2 for Validating Hashes`_                                                                            | SV-86697            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-021620      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Verify and Correct Ownership with RPM`_                                                                                             | SV-86473            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-010010      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Verify and Correct File Permissions with RPM`_                                                                                      | SV-86473            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-010010      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD`_                                                             | SV-86571            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-010340      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Operating system must display the date and time of the last successful account logon upon logon`_                                   | SV-86899            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-040530      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Operating system must be configured so that the audit system takes appropriate action when the audit storage volume is full`_       | SV-86711            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-030320      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `Operating system must be configured to off-load audit logs onto a different system or storage media from the system being audited`_ | SV-95729            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-030201      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `User Must Not Be Allowed To Change Password More-frequently than once per 24 hours`_                                                | SV-86551            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-010240      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `User Must Change Password At Least Once Every Sixty Days`_                                                                          | SV-86555            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-010260      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `User Must Be Provided Adequate Warning Of Password-Expiration`_                                                                     |                     |
  |                                                                                                                                      |                     |
  |                                                                                                                                      |                     |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `User Account Must Be Expired N Days After Password Has Expired`_                                                                    | SV-86565            |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-010310      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `For Operating Systems Using DNS Resolution, At Least Two Name Servers Must Be Configured`_                                          | SV-204608           |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-040600      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+
  | `The OS Must Elevate The SELinux Context When An Administrator Calls The Sudo Command`_                                              | SV-250314           |
  |                                                                                                                                      |                     |
  |                                                                                                                                      | RHEL-07-020023      |
  +--------------------------------------------------------------------------------------------------------------------------------------+---------------------+

```

# Use Only FIPS 140-2 Validated Ciphers

**Invalid Finding:**

Watchmaker implements setting valid through EL7 STIGv2R6 (released: October 2019)

# Use Only FIPS 140-2 Validated MACs 

Invalid Finding:  Watchmaker implements setting valid through EL7 STIGv2R6 (released: October 2019)

# Modify the System Login Banner

**Invalid Finding:**

Watchmaker implements site-prescribed banner. Scan-profile's regex may not be flexible enough to match the site-prescribed banner as implemented by watchmaker.

# Enable Smart Card Login

**Conditionally-Valid Finding:**

Smart Card Login use and configuration is site-specific. Site has not provided specification for implementing this setting within scanned context.

# Configure the Firewalld Ports

**Invalid Finding:**

Watchmaker implements setting. However, scanner regex may not be sufficiently-flexible in its specification.

# Set Default firewalld Zone for Incoming Packets

**Conditionally-Valid Finding:**

Enabling "drop" as the default firewald zone breaks things like ping-sweeps (used by some IPAM solutions, security-scanners, etc.). Some sites will request the "drop" zone not be used. Scan-profiles should be updated to reflect the need to not have "drop" be the active zone.

# Disable Kernel Parameter for IP Forwarding

**Invalid Finding:**

The prescribed `net.ipv4.ip_forward` value is set by watchmaker in `/etc/sysctl.d/99-sysctl.conf`. Executing `sysctl net.ipv4.ip_forward` on watchmaker-hardened system returns expected `net.ipv4.ip_forward = 0` result

# The Installed Operating System Is Vendor Supported

**Invalid Finding:**

No programmatic validation or remediation prescribed or universally-implementable: requires manual validation with OS-vendor lifecycle information page(s). 

# Install McAfee Virus Scanning Software

**Conditionally-Valid Finding:**

* Where configured to do so, watchmaker will install HBSS or VSEL. Any scan-findings on systems watchmaker has been configured to install HBSS or VSEL are typically due to version mismatches between installed and scanned-for versions
* Where required/scanned for but not installed, site will need to specify automatable installation-method that will produce match againste scanned-for configuration
* Where not required, scanner should either be reconfigured not to scan for presence or scan-results should be ignored

# Enable FIPS Mode in GRUB2

**Conditionally-Valid Finding:**

Both spel and watchmaker implement `fips=1` by default. If finding occurs, either:

* There is an error in scanner's validation-method
* System has been intentionally de-configured for FIPS &mdash; typically due to hosted-software's requirements &mdash; and scanned-system will need to be granted a deployment security-exception.

# Configure AIDE to Use FIPS 140-2 for Validating Hashes

**Invalid Finding:**

Because there is more than one way to implement this setting, scanners typically do not perform a real scan for this setting. Instead some scanners implement a null-test to flag the configuration-item to try to force a manual review. Watchmaker implements this configuration-titem by setting `NORMAL = FIPSR+sha512` in the `/etc/aide.conf` file: may be manually validated by executing `grep NORMAL\ = /etc/aide.conf`.

# Verify and Correct Ownership with RPM

**Invalid Finding:**

* Flags on system-journal ownership: Journal ownership settings are automatically reset by systemd (upon reboot) after hardening has run. Currently, no means of permanently remediating is possible.
* Similarly, if HBSS or VSEL is installed, scan may flag on user-ownership depending on how site specifies installation of HBSS or VSEL. One would reasonably expect similar for other, third-party packages.  "Fixing" (per STIG guidance) would likely break the functioning of the HBSS/VSEL (or third-party) software

# Verify and Correct File Permissions with RPM

**Invalid Finding:**

* Flags on system-journal ownership: Journal ownership settings are automatically reset by systemd (upon reboot) after hardening has run. Currently, no means of permanently remediating is possible.
* May also flag on vendor-delivered CA-trust files which are dynamicly-injected into relevant trust-stores. Currently, no known means of permanently remediating is possible.
* May flag on third-party tools' (e.g., Splunk) config, log and other files

# Ensure Users Re-Authenticate for Privilege Escalation - sudo NOPASSWD

**Conditionally-Valid Finding:**

Flagged-configuration is frequently required for properly enabling a "break-glass" account at provisioning-time. This is especially so in consoleless environments (like AWS). Disable scan or ignore scan-findings when such accounts are required.

# Operating system must display the date and time of the last successful account logon upon logon

**Invalid Finding:**

Some scanners implement a scan equivalent to:

```
grep -P '^[\s]*[^\s#]+[ \t]+[\[\]\w=]+[ \t]+pam_lastlog\.so[ \t]+([\S \t]+)\s*$' /etc/pam.d/postlogin
```

To try to determine if PAM's `showfailed` module is properly activated. These scanners typically only expect a single line of output that looks like:

```
session    required       pam_lastlog.so showfailed
```

However, on a system that watchmaker has been applied to, the scan-return will typically look like:

```
session    required       pam_lastlog.so showfailed
session    [default=1]    pam_lastlog.so nowtmp showfailed
session    optional       pam_lastlog.so silent noupdate showfailed
```

If the scanner does not properly handle this multi-line output, it will report a failure even though the required configuration-fixes are actually in place and functioning as desired.

# Operating system must be configured so that the audit system takes appropriate action when the audit storage volume is full

**Invalid Finding:**

The `disk_full_action` _is_ configured. However, it is not configured where scanners may be configured to look for it. The STIG-prescribed method expects configuration through the `audisp-remote` subsystem. Since configuration of the `audisp-remote` subsystem is inherently site-specific, generic executions of watchmaker do not attempt to configure it. Instead, watchmaker handles the `disk_full_action` configuration-item via the _main_ audit subsystem. This can be confirmed by executing:

```
( find /etc/audisp -type f ; find /etc/audit -type f ) | xargs grep disk_full_action
```

Executing the above _should_ return something like:

```
/etc/audit/auditd.conf:disk_full_action = SUSPEND
```
# Operating system must be configured to off-load audit logs onto a different system or storage media from the system being audited

**Invalid Finding:**

Configuration of the `audisp-remote` subsystem is inherently site-specific: quite frequently, the `audisp-remote` subsystem is wholly supplanted by other offload-methods (e.g., Splunk, FluentBit, CloudWatch Logs, etc.). Therefore, neither generic executions of watchmaker nor executions that include configuration of `audisp-remote` alternatives will attempt to configure it.

# User Must Not Be Allowed To Change Password More-Frequently than once per 24 hours

Typically caused when a user is created via a service/process like `cloud-init`: the resulting user may not have its password-aging `mindays` parameter (field #4 in `/etc/shadow`) set

# User Must Change Password At Least Once Every Sixty Days

Typically caused when a user is created via a service/process like `cloud-init`: the resulting user may not have its password-aging `maxdays` parameter (field #5 in `/etc/shadow`) set

# User Must Be Provided Adequate Warning Of Password-Expiration

Typically caused when a user is created via a service/process like `cloud-init`: the resulting user may not have its password-aging `warndays` parameter (field #6 in `/etc/shadow`) set

# User Account Must Be Expired N Days After Password Has Expired

Typically caused when a user is created via a service/process like `cloud-init`: the resulting user may not have its password-aging `inactivedays` parameter (field #7 in `/etc/shadow`) set

# For Operating Systems Using DNS Resolution, At Least Two Name Servers Must Be Configured

**Conditionally Valid:**

Only valid in environments where individually-defined DNS servers are not highly-available.

When deployed into environments where DNS is provided through a highly-available service with a highly-available service-name, only one DNS server will be configured into the host's `/etc/resolv.conf` &ndash; typically by way of a DHCP option-set.

# The OS Must Elevate The SELinux Context When An Administrator Calls The Sudo Command

**Conditionally Valid:**

Implementation of this finding's technical controls changes how the `sudo` commands are executed. Some EL7 tooling (at least one third-party authentication subsystem is known to break under this new control) is incompatible with implementing this control. For systems where this control breaks functionality, and must be disabled, this will be a valid finding that should be included in any exception documentation and associated organizational-processes. Otherwise the system should be configured to meet this control.

**Further Notes:**

1. Implementing this control can have significant user-education requirements and can also adversely-impact legacy automation. While these _should_ be non-fatal problems &ndash; only requiring user-education or fine-tuning of legacy automation, the control still should be implemented.
1. As implemented in this project, the modifications to the relevnt `/etc/sudoers.d` files may create sub-optimal SELinux transistions. If so, it will be up to the watchmaker-user to deactivate the `ash-linux.el7.STIGbyID.cat2.RHEL-07-020023` (see the [pillar.example file](https://github.com/plus3it/ash-linux-formula/blob/master/pillar.example) in the [ash-linux-formula](https://github.com/plus3it/ash-linux-formula) project; see also the associated [README](https://github.com/plus3it/ash-linux-formula/blob/master/README_PillarContents.md#skip-stigs) file for further elaboration) and then provide their own mapping-modifications as a substitute. Deactivation can be done via the `ash-linux:lookup:skip-stigs` list-variable in Pillar.
