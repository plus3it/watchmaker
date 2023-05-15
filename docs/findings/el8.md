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
  .. _Prevent System Daemons From Using Kerberos For Authentication: #prevent-system-daemons-from-using-kerberos-for-authentication
  .. _Users Must Provide A Password For Privilege Escalation: #users-must-provide-a-password-for-privilege-escalation
  .. _A Separate Filesystem Must Be Used For the <tt>/tmp</tt> Directory: #a-separate-filesystem-must-be-used-for-the-tmp-directory
  .. _The OS must mount <tt>/tmp</tt> with the nodev option: #the-os-must-mount-`/tmp`-with-the-nodev-option
  .. _The OS must mount <tt>/tmp</tt> with the <tt>nosuid</tt> option: #the-os-must-mount-`/tmp`-with-the-nosuid-option
  .. _The OS must mount <tt>/tmp</tt> with the <tt>noexec</tt> option: #the-os-must-mount-`/tmp`-with-the-noexec-option
  .. _The OS Must Ensure Session Control Is Automatically Started At Shell Initialization: #the-os-must-ensure-session-control-is-automatically-started-at-shell-initialization
  .. _User Account Passwords Must Be Restricted To A 60-Day Maximum Lifetime: #user-account-passwords-must-be-restricted-to-a-60-day-maximum-lifetime
  .. _OS Must Be Configured In The Password-Auth File To Prohibit Password Reuse For A Minimum Of Five Generations: #os-must-prohibit-password-reuse-for-a-minimum-of-five-generations
  .. _The Installed Operating System Is Not Vendor Supported: #the-installed-operating-system-is-not-vendor-supported
  .. _All Content In A User's Home Directory Must Be Group-Owned By The Primary User: #all-user-content-in-a-user's-home-directory-must-be-group-owned-by-the-primary-user
  .. _"Only Authorized Local User Accounts Exist on Operating System" is always flagged: #only-authorized-local-user-accounts-exist-on-operating-system"-is-always-flagged
  .. _All Interactive User Home Directory Files Must Be Mode 0750 Or Less Permissive: #all-interactive-user-home-directory-files-must-be-mode-0750-or-less-permissive
  .. _Add nosuid Option to /boot: #add-nosuid-option-to-/boot
  .. _Configure Multiple DNS Servers in /etc/resolv.conf: #configure-multiple-dns-servers-in-/etc/resolv.conf
  .. _Enable Certmap in SSSD: #enable-certmap-in-sssd
  .. _Verify that Shared Library Directories Have Root Ownership: #verify-that-shared-library-directories-have-root-ownership
  .. _Oracle Linux 8 STIGs Specify Conflicting ClientAliveCountMax values: #oracle-linux-8-stigs-specify-conflicting-clientalivecountmax-values
  .. _Record Events When Privileged Executables Are Run: #record-events-when-privileged-executables-are-run

  +--------------------------------------------------------------------------------------------+---------------------+
  | Finding Summary                                                                            | Finding Identifiers |
  +============================================================================================+=====================+
  | `Prevent System Daemons From Using Kerberos For Authentication`_                           | V-230238            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010161      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `Users Must Provide A Password For Privilege Escalation`_                                  | V-230271            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010380      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `A Separate Filesystem Must Be Used For the /tmp Directory`_                               | V-230295            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010543      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `The OS must mount /tmp with the nodev option`_                                            | V-230511            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-040123      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `The OS must mount /tmp with the nosuid option`_                                           | V-230512            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-040124      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `The OS must mount /tmp with the noexec option`_                                           | V-230514            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-040125      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `The OS Must Ensure Session Control Is Automatically Started At Shell Initialization`_     | V-230349            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-020041      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `User Account Passwords Must Be Restricted To A 60-Day Maximum Lifetime`_                  | V-230367            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-020210      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `OS Must Prohibit Password Reuse For A Minimum Of Five Generations`_                       | V-230368            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-020220      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `The Installed Operating System Is Not Vendor Supported`_                                  | V-230221            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010000      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `All Content In A User's Home Directory Must Be Group-Owned By The Primary User`_          | V-244532            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010741      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `"Only Authorized Local User Accounts Exist on Operating System" is always flagged`_       | V-230379            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-020320      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `All Interactive User Home Directory Files Must Be Mode 0750 Or Less Permissive`_          | V-244531            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010731      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `Add nosuid Option to /boot`_                                                              | V-230300            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010571      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `Configure Multiple DNS Servers in /etc/resolv.conf`_                                      | V-230316            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010680      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `Enable Certmap in SSSD`_                                                                  | V-230355            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-020090      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `Verify that Shared Library Directories Have Root Ownership`_                              | V-251709            |
  |                                                                                            |                     |
  |                                                                                            | RHEL-08-010351      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `Oracle Linux 8 STIGs Specify Conflicting ClientAliveCountMax values`_                     | V-248552            |
  |                                                                                            |                     |
  |                                                                                            | OL08-00-010200      |
  +--------------------------------------------------------------------------------------------+---------------------+
  | `Record Events When Privileged Executables Are Run`_                                       | V-248722            |
  |                                                                                            |                     |
  |                                                                                            | OL08-00-030000      |
  +--------------------------------------------------------------------------------------------+---------------------+
```


# Prevent System Daemons From Using Kerberos For Authentication

**Condtionally-valid Finding:**

If an EL8 system is bound to Active Directory &ndash; or other Kerberos-enabled centralized authentication-source &ndash; or is _acting as_ a Kerberos domain controller (KDC), the presence of an `/etc/krb5.keytab` file is mandatory.

If the scanned system does not have the `krb5-workstation` or `krb5-server` packages installed and _any_ `.keytab` files are found in the `/etc` directory, this is a valid finding.

# Users Must Provide A Password For Privilege Escalation

**Condtionally-valid Finding:**

If a `sudo`-enabled user is password-enabled, they should be prompted for that password in order to escalate privileges.

If a `sudo`-enabled user is _not_ password-enabled (e.g, if the user is used only with key- or token-based authentication), they should not be prompted for any password. Forcing use of passwords for `sudo`-enabled users that do not have passwords will render those user-accounts unable to escalate privileges. Failure to exempt such users will render "break glass" and similar accounts not usable for their intended function.

# A Separate Filesystem Must Be Used For the `/tmp` Directory

**Invalid Finding:**

When using Amazon Machine Images, Azure VM-templates, or the like, that have been built using the [spel automation](https://github.com/plus3it/spel), the `/tmp` directory in the resultant EC2 (VM, etc.) is hosted on a psuedo-filesystem of type `tmpfs`. This is done using the `tmp.mount` systemd unit. Many security-scanning tools that look for `/tmp`-related mount-information do not know how to properly scan when `tmp` is used this way and will, as a result, report a (spurious) finding.

**Proof of Correctness:**

To validate that the required-setting is _actually_ present, execute:

~~~
grep -w /tmp /proc/mounts
~~~

If this returns null, the scan-result is valid; otherwise the scan-result is _invalid_.

# The OS must mount `/tmp` with the `nodev` option

**Invalid Finding:**

When using Amazon Machine Images, Azure VM-templates, or the like, that have been built using the [spel automation](https://github.com/plus3it/spel), the `tmp.mount` systemd unit is used to manage mounting of the `tmpfs`-based `/tmp` directory. Mount options &ndash; such as `nodev` &ndash; are defined through two files:

- `/usr/lib/systemd/system/tmp.mount`: This file contains the vendor-defined defaults and is installed via the `systemd` RPM
- `/etc/systemd/system/tmp.mount.d/options.conf`: This file is installed via watchmaker's state-handler, `ash-linux.el8.STIGbyID.cat2.RHEL-08-040123`. This file overrides the values held in the vendor-managed `systemd` RPM's file

Many security-scanners do not know how to find the mount-options for the `/tmp` (pseudo) filesystem when it is managed via systemd and uses these files to set the mount options. As a result, such scanners will report a (spurious) finding

**Proof of Correctness:**

To validate that the required-setting is _actually_ present, execute:

~~~
grep -w /tmp /proc/mounts | grep nodev
~~~

If this returns null, the scan-result is valid; otherwise the scan-result is _invalid_.

# The OS must mount `/tmp` with the `nosuid` option

**Invalid Finding:**

As with the "<i><a href="#the-os-must-mount-`/tmp`-with-the-nodev-option">The OS must mount `/tmp` with the nodev option</a></i>" finding, this finding is due to an incompatibility between how the scanner checks for the setting and how the setting is actually implemented.

**Proof of Correctness:**

To validate that the required-setting is _actually_ present, execute:

~~~
grep -w /tmp /proc/mounts | grep nosuid
~~~

If this returns null, the scan-result is valid; otherwise the scan-result is _invalid_.

# The OS must mount `/tmp` with the `noexec` option

**Invalid Finding:**

As with the "<i><a href="#the-os-must-mount-`/tmp`-with-the-nodev-option">The OS must mount `/tmp` with the nodev option</a></i>" finding, this finding is due to an incompatibility between how the scanner checks for the setting and how the setting is actually implemented.

**Proof of Correctness:**

To validate that the required-setting is _actually_ present, execute:

~~~
grep -w /tmp /proc/mounts | grep noexec
~~~

If this returns null, the scan-result is valid; otherwise the scan-result is _invalid_.

# The OS Must Ensure Session Control Is Automatically Started At Shell Initialization

**Invalid Finding:**

As implemented, watchmaker places an `/etc/profile.d/tmux.sh` file that looks like:

~~~
# Check if shell is interactive
if [[ $- == *i* ]] && [[ $( rpm --quiet -q tmux )$? -eq 0 ]]
then
   parent=$( ps -o ppid= -p $$ )
   name=$( ps -o comm= -p $parent )

   # Check if controlling-process is target-value
   case "$name" in
      sshd|login)
         exec tmux
         ;;
   esac
fi
~~~

This file addresses the concerns of the STIG finding-ID, but does so in a functionally-safer way. The additional 'safing' included in the watchmaker-placed script may cause scanners that are too-inflexibly coded to spuriously declare a finding.

# User Account Passwords Must Be Restricted To A 60-Day Maximum Lifetime

**Invalid Finding:**

Some, locally-managed user's accounts are configured _only_ for token-based logins (SSH keys, GSSAPI, etc.). The accounts are typically configured with no passwords. Some of these accounts also serve a "break-glass" function. If passwordless accounts are configured with password-expiry enabled, they may become no longer fit for purpose once they've reached their expiry.

Many scanners are not adequately configured to differentiate between passwordless and password-enabled locally-managed accounts. Typically, poorly-configured scanners will execute a compliance-test equivalent to:

~~~
awk -F: '$5 > 60 { print $1 " " $5 }' /etc/shadow
awk -F: '$5 <= 0 { print $1 " " $5 }' /etc/shadow
~~~

Or, expressed more compactly:

~~~
awk -F: '$5 > 60 || $5 <= 0 { print $0 }' /etc/shadow
~~~

If so, such scanners will assert a finding that is not actually valid for locked-password accounts.

**Proof of Correctness:**

To validate that passwordless accounts are properly configured, instead execute:

~~~
awk -F: '$2 !~ /^[!*]*/ && ( $5 > 60 || $5 <= 0 ) { print $0 }' /etc/shadow
~~~

The above adds the further check of each line of the `/etc/shadow` file's second field (hashed password string) for the tokens indicating a locked-password account (`!` and/or `*`). Adding this further check should yield a null return

# OS Must Prohibit Password Reuse For A Minimum Of Five Generations

**Invalid Finding:**

This is a spurious finding. Per the STIG, `watchmaker` updates the `/etc/pam.d/password-auth` file to ensure the presence of a `remember=5` token on the file's `password required pam_pwhistory.so` line:

* If a line exists starting with `password required pam_pwhistory.so` but has a non-conformant value for the `remember=` token, the non-conformant value is replaced with `5`
* If a line exists starting with `password required pam_pwhistory.so` but has no `remember=` token, one with a suitable value is appended
* If a line starting with `password required pam_pwhistory.so` does not exist, one is created with _only_ the `remember=5` token present

Some scanners _may_ be configured to look for a greater number of tokens set than _just_ the `remember=5` token. E.g., some may look for something more like:

~~~
password required pam_pwhistory.so use_authtok remember=5 retry=3
~~~

**Proof of Correctness:**

To validate that the required `remember=5` is present, execute:

~~~
grep -l -n remember=5 $( readlink -f /etc/pam.d/password-auth )
~~~

The above _should_ return either `/etc/authselect/password-auth` or `/etc/pam.d/password-auth`; if the above has a null return, re-execute the `ash-linux.el8.STIGbyID.cat2.RHEL-08-020221` Saltstack state and re-validate.

# The Installed Operating System Is Not Vendor Supported

**Expected Finding:**

This rule effects primarily "free" versions of the Red Hat Enterprise Linux operating system. This result is expected on the CentOS 8 &ndash; "Core" or "Stream" &ndash; Rocky and Alma linux distributions. Scanners that highlight this finding are looking for the presence of any _one_ of the following RPMs:

* `redhat-release-client`
* `redhat-release-server`
* `redhat-release-workstation`
* `redhat-release-computenode`
* `redhat-release-virtualization-host`
* `oraclelinux-release`
* `sled-release`
* `sles-release`

And an `/etc/redhat-release` file with contents that aligns to one that's delivered with any of the preceding RPM. The various "free" versions of the Red Hat Enterprise Linux operating system will not have any of the above RPMs present.

If using a vendor-supported Linux and this scan finding occurs, it's likely that either the `release-` RPM is missing or damaged, something has unexpectedly altered the target's `/etc/redhat-release` file or the scanner is looking for a wildcarded `release` file under the `/etc`  directory and there's an unexpected filename found.

# All Content In A User's Home Directory Must Be Group-Owned By The Primary User

**Expected Finding:**

At initial scan, this finding is typically triggered by the installation of some standard "enterprise" services. Some of these services, due to how they execute, will create _some_ of their files with `root` as the user- and/or (more importantly for this finding) group-owner.

The `oscap` content for this finding includes the caveat:

> _Due to OVAL limitation, this rule can report a false negative in a specific situation where two interactive users swap the group-ownership of folders or files in their respective home directories._

While not a 100% overlap to the reason offered here, the caveat covers a common scenario. Other common scenarios may include:

* Unpacking of archive files authored on a different system
* Restoration of a user's `${HOME}` from another system to the current (scanned) system

In either of these further cases, such will most typically only show up on lifecycle scans and not provisioning-time scans

# "Only Authorized Local User Accounts Exist on Operating System" is always flagged

**Expected Finding:**

Per the STIG notes:

> _Automatic remediation of this control is not available due to the unique requirements of each system._

While-automation _could_ be authored that would leverage a site- or host-specific allowed-users list to disable or delete forbidden accounts, there exists an extremely-high likelihood that scanners used against such configuration-controlled operating environments would not contain the scanning logic necessary to validate compliance. As such &ndash; and with or without user-controlling automation-content &ndash; STIG scanners would still flag systems that are _technically_ compliant.

# All Interactive User Home Directory Files Must Be Mode 0750 Or Less Permissive

**Expected Finding:**

Some scanners will erroneously alert on this for either/both of two reasons:

- The scanner is looking for files that have mode-zero for their "all" field regardless of owning-directory's mode-setting: in this case, the result is _technically_ a correct finding but, from an _effective_ security perspective is non-problematic
- The scanner may be confused if the "failed" file's group-permission is zero: in this case, the result is simply not valid

# Add `nosuid` Option to `/boot`

**Invalid Finding:**

Some scanners will check to see what the mount-option is for the filesystem containing the `/boot` directory without first ensuring that `/boot` directory is actually a standalone filesystem. When `/boot` is not a standalone filesystem, it gets the same boot-options as the `/` filesystem and, therefore, cannot have the `nosuid` mount-option set.

# Configure Multiple DNS Servers in `/etc/resolv.conf` 

**Expected Finding:**

When deploying EL8 systems into environments with highly-available DNS servers, the system will typically only have _one_ DNS server configured.

# Enable Certmap in SSSD

**Invalid Finding:**

This finding is intended to result in a manual configuration-validation of the target system. Scanners that flag this finding typically include a note like:

> _Automatic remediation of this control is not available since all of the settings in the certmap need to be customized_

Further, configuration of the `sssd` certmap is typically required only for systems that are configured for _direct_ authentication via client-certificate. This configuration-method is typically done only for systems with locally-attached SmartCard/PIV readers. "Remote" systems (such as those hosted with a CSP like AWS or Azure) typically _indirectly_ authenticate with client-certificates (either through SSH key-forwarding or GSSAPI token-forwarding).

# Verify that Shared Library Directories Have Root Ownership

**Expected Finding:**

Some applications and/or enterprise-integration tools may install private shared-libraries that are user- or group- owned by the installed-application. The scanner may identify these as insecure/improperly-owned, regardless of permission-setting on higherl-level directories.

# Oracle Linux 8 STIGs Specify Conflicting `ClientAliveCountMax` values

**Conflicting Guidance:**

As of the time of this section's writing, there is a disagreement between the DISA STIG's target-value for the SSH daemon's `ClientAliveCountMax` value and that specified via the STIG's upstream content-project, Compliance As Code. The former specifies that the parameter's value should be `1`; the latter specifies that it should be `0`. This project's hardening implements the former as that is also the value specified by both the DISA STIG's and Compliance As Code project's recommended setting for Red Hat Linux 8.

# Record Events When Privileged Executables Are Run

**Invalid Finding:**

Some security-scanners misidentify the compliance-state of target-systems for vulnerability-ID, V-248722 (OL08-00-030000). The relevant STIG check-text should be either or both of:

- `grep execve /etc/audit/audit.rules`
- `grep -r execve /etc/audit/rules.d`

After watchmaker is applied, the former returns:

```
-a always,exit -F arch=b32 -S execve -C gid!=egid -F key=setgid
-a always,exit -F arch=b64 -S execve -C gid!=egid -F key=setgid
-a always,exit -F arch=b32 -S execve -C uid!=euid -F key=setuid
-a always,exit -F arch=b64 -S execve -C uid!=euid -F key=setuid
```

While the latter returns:

```
/etc/audit/rules.d/setuid.rules:-a always,exit -F arch=b32 -S execve -C uid!=euid -F key=setuid
/etc/audit/rules.d/setuid.rules:-a always,exit -F arch=b64 -S execve -C uid!=euid -F key=setuid
/etc/audit/rules.d/setgid.rules:-a always,exit -F arch=b32 -S execve -C gid!=egid -F key=setgid
/etc/audit/rules.d/setgid.rules:-a always,exit -F arch=b64 -S execve -C gid!=egid -F key=setgid
```

It is the presence of the content in the file in the `/etc/audit/rules.d/` directory that results in &ndash; by way of the `augenrules` service &ndash; the presence of the correct content in the `/etc/audit/audit.rules` file.