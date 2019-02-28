.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com

.. |sshdconfig| replace:: ``sshd_config (5)``
.. _sshdconfig: https://linux.die.net/man/5/sshd_config

## `sshd_config` Parameter Values

### `LogLevel` Parameter's Value Not Set to `INFO` in `/etc/ssh/sshd_config`

The "stock" `/etc/ssh/sshd_config` file typically contains a commented-out line for the `LogLevel` parameter similar to the following:

~~~
[...elided...]

#SyslogFacility AUTH
SyslogFacility AUTHPRIV
#LogLevel INFO

# Authentication:

[...elided...]
~~~

When the vendor includes a commented-out parameter-value in the configuration-file, it signifies that the paramter is set to the value shown on the commented out line. This can be further confirmed by consulting the associated manual page (see: |sshdconfig|_):

~~~
     LogLevel
             Gives the verbosity level that is used when logging messages from
             sshd(8).  The possible values are: QUIET, FATAL, ERROR, INFO,
             VERBOSE, DEBUG, DEBUG1, DEBUG2, and DEBUG3.  The default is INFO.
             DEBUG and DEBUG1 are equivalent.  DEBUG2 and DEBUG3 each specify
             higher levels of debugging output.  Logging with a DEBUG level
             violates the privacy of users and is not recommended.
~~~

Note: _If it is desired to alter from the default_, it is typically recommended to change to `VERBOSE` — particularly if key-based logins are in use. This setting will cause the SSH daemon to record the fingerprints of presented-keys.

### `MACs` Parameter Values Not Compliant

The watchmaker-initiated remediation sets a STIG-valid value for the `MACs` parameter, however, the `oscap` utility's validity-regex incorrectly flags the set value as incorrect.

A bug for a prior faulty regex was opened with the vendor in 2017 and closed in September of 2018. However, even with the fixed content, the regex is still incorrectly flagging the set value as incorrect. A new [bug](https://bugzilla.redhat.com/show_bug.cgi?id=1684086) has been opened with vendor. Until it is resolved, this finding should be considered spurious.

### `Ciphers` Parameter Values Not Compliant

The watchmaker-initiated remediation sets a STIG-valid value for the `Ciphers` parameter, however, the `oscap` utility's validity-regex incorrectly flags the set value as incorrect.

A bug for a prior faulty regex was opened with the vendor, remediated in the upstream project and the vendor-bug closed. However even with the fixed content, the regex is still incorrectly flagging the set value as incorrect. A new [bug](https://bugzilla.redhat.com/show_bug.cgi?id=1684086) has been opened with vendor. Until it is resolved, this finding should be considered spurious.

## System Login Banner Is Missing or Incorrect

Watchmaker sets the system login banners per STIG guidance. However, many validation-tools' pattern-matches are failure-prone. These scanner-errors may be ignored (or documented/excepted). The presence of banner contents is easily verifiable:

- Perform an SSH-based login: the banner will be displayed. (Note: _do not_ configure the SSH client to suppress the display of the remote server's banners during verification)
- Login and view the contents of the `/etc/issue` file (note: findings related to GNOME not relevant on headless systems)

## Ensure All SUID Executables Are Authorized

Some scanners implement an "intentional fail" for this audit-item. This is designed to force the acrediting-staff to manually examine a system for the presence of _unexpected_ SUID files.

This automation has the underlying assumption that all RPM-managed SUID files — be it by the OS vendor or the provider of the software _hosted by_ the OS — is implicitly authorized. A  way to quickly-verify compliance with this assumption is to execute:

~~~
for SUID in $( find / -user root -perm -4000 -print 2> /dev/null )
do
   printf "%s: " "${SUID}"
   rpm --qf '%{name}\t%{vendor}\n' -qf "$SUID"
done | awk '{printf("%-40s\t%-12s\t%s\n",$1,$2,$3)}'
~~~

Executing the above will output a list similar to:

~~~
/usr/bin/passwd:                                passwd          CentOS
/usr/bin/pkexec:                                polkit          CentOS
/usr/bin/crontab:                               cronie          CentOS
/usr/bin/mount:                                 util-linux      CentOS
/usr/bin/su:                                    util-linux      CentOS
/usr/bin/umount:                                util-linux      CentOS
/usr/bin/chfn:                                  util-linux      CentOS
/usr/bin/chage:                                 shadow-utils    CentOS
/usr/bin/chsh:                                  util-linux      CentOS
/usr/bin/newgrp:                                shadow-utils    CentOS
/usr/bin/gpasswd:                               shadow-utils    CentOS
/usr/bin/sudo:                                  sudo            CentOS
/usr/sbin/pam_timestamp_check:                  pam             CentOS
/usr/sbin/usernetctl:                           initscripts     CentOS
/usr/sbin/unix_chkpwd:                          pam             CentOS
/usr/lib/polkit-1/polkit-agent-helper-1:        polkit          CentOS
/usr/libexec/dbus-1/dbus-daemon-launch-helper:  dbus            CentOS
~~~

If any listed files are not displayed as being from the OS-vendor (typically "CentOS" or "RedHat") or the vendor of the hosted application, investigate further to determine if the file meets site-specific authorization-criteria.

Note: If the site has policies that are more stringent than the "all SUID files associated with an OS-vendor RPM are valid", a manual scan and remediation will likely be required. This is outside of the scope of this document and will not be satisfiable with this tool's hardening automation.

## Missing Mount Options

Third-party security scanners will frequently call out missing filesystem mount options. The following sub-sections provide explanations for this condition.

### `/dev/shm` — `noexec` Option MISSING

This is a scan error — most likely due to an improperly-formatted search-expression. The watchmaker utilities set the `noexec` Option for `/dev/shm` Pseudo-Filesystem in the `/etc/fstab` configuration file. This can be verified with the following commands.

~~~
grep -E '\s\/dev\/shm\s.*noexec' /proc/mounts
grep -E '\s\/dev\/shm\s.*noexec' /etc/fstab
~~~

The above verifies that the mounted `/dev/shm` has the desired mount-option set and that the setting will persist after a reboot.

### `/tmp` — `nodev` Option Missing

This is a false-finding. Many scanning tool assume that `/tmp` will be a standard, disk-based filesystem. The OSes typically hardened via Watchmaker do not use a standard, disk-based filesystem for `/tmp`. Instead, `/tmp` is implemented as a pseudo-filesystem via the `tmp.mount` systemd service.

Because scanners typically assume that `/tmp` will be a standard, disk-based filesystem, they will typically scan the contents of the `/etc/fstab` file to ensure compliance. When `/tmp` is managed via the `tmp.mount` systemd service, there will be no entry for the `/tmp` filesystem in the `/etc/fstab` file. This creates a false scan-error. The correct scan-method is to look for the `nodev` option in the `/etc/systemd/system/tmp.mount.d/options.conf` configuration file, instead.

To properly verify that Watchmaker has applied the required mount-option to the systemd-managed `/tmp` mount:

~~~
grep -E '\s\/tmp\s.*nodev' /proc/mounts
grep nodev /etc/systemd/system/tmp.mount.d/options.conf
~~~

The above verifies that the mounted `/tmp` has the desired mount-option set and that the setting will persist after a reboot.

### `/tmp` — `noexec` Option Missing

This is a false-finding. Many scanning tool assume that `/tmp` will be a standard, disk-based filesystem. The OSes typically hardened via Watchmaker do not use a standard, disk-based filesystem for `/tmp`. Instead, `/tmp` is implemented as a pseudo-filesystem via the `tmp.mount` systemd service.

Because scanners typically assume that `/tmp` will be a standard, disk-based filesystem, they will typically scan the contents of the `/etc/fstab` file to ensure compliance. When `/tmp` is managed via the `tmp.mount` systemd service, there will be no entry for the `/tmp` filesystem in the `/etc/fstab` file. This creates a false scan-error. The correct scan-method is to look for the `noexec` option in the `/etc/systemd/system/tmp.mount.d/options.conf` configuration file, instead.

To properly verify that Watchmaker has applied the required mount-option to the systemd-managed `/tmp` mount:

~~~
grep -E '\s\/tmp\s.*noexec' /proc/mounts
grep noexec /etc/systemd/system/tmp.mount.d/options.conf
~~~

The above verifies that the mounted `/tmp` has the desired mount-option set and that the setting will persist after a reboot.

### `/tmp` — `nosuid` Option Missing

This is a false-finding. Many scanning tool assume that `/tmp` will be a standard, disk-based filesystem. The OSes typically hardened via Watchmaker do not use a standard, disk-based filesystem for `/tmp`. Instead, `/tmp` is implemented as a pseudo-filesystem via the `tmp.mount` systemd service.

Because scanners typically assume that `/tmp` will be a standard, disk-based filesystem, they will typically scan the contents of the `/etc/fstab` file to ensure compliance. When `/tmp` is managed via the `tmp.mount` systemd service, there will be no entry for the `/tmp` filesystem in the `/etc/fstab` file. This creates a false scan-error. The correct scan-method is to look for the `nosuid` option in the `/etc/systemd/system/tmp.mount.d/options.conf` configuration file, instead.

To properly verify that Watchmaker has applied the required mount-option to the systemd-managed `/tmp` mount:

~~~
grep -E '\s\/tmp\s.*nosuid' /proc/mounts
grep nosuid /etc/systemd/system/tmp.mount.d/options.conf
~~~

The above verifies that the mounted `/tmp` has the desired mount-option set and that the setting will persist after a reboot.

### `/var/tmp` — `nodev` Option Missing

Cannot satisfy: `/var/tmp` not implemented as stand-alone filesystem.

Typically, STIG guidance recommends not that `/var/tmp` be a truly standalone filesystem but as a bind-mount of `/var/tmp`. When so implemented, `/var/tmp` inherits the same mount-options used for `/tmp`. Industry best-practices around the implementation of `/tmp` and `/var/tmp` is that the former is ephemeral — contents disappear at each boot and/or by way of a "`/tmp` cleaner" process &dash; while the contents of `/var/tmp` are non-ephemeral. Further, most Enterprise Linux users expect the contents of `/var/tmp` to be non-ephemeral. Because `/tmp` is a VMS-based pseudo-filesystem, the only way to meet both the industry best-practices guidance and user assumptions for `/var/tmp` is to _not_ make `/var/tmp` a bind-mount of `/tmp`. Because the STIGs fail to specify "`/var` must be a standalone filesystem" and not wishing to waste further disk-space to create a `/var/tmp` separate from the `/var` filesystem, `/var/tmp` is typically left as a subdirectory of the `/var` filesystem. This means that `/var/tmp` has no mount options of its own. The only appicable mount options are those inherited from the parent `/var` filesystem.

Note: for programs that place the additional requirement that `/var/tmp` _must_ be a standalone filesystem, it is recommended to up the size of the root volume-group, create an LVM volume to host the `/var/tmp` filesystem and then apply the site-local mount-options to the filesystem. This can all be accomplished at system provisioning-time, but is outside the scope of the watchmaker utility to effect.

### `/var/tmp` — `noexec` Option Missing

Cannot satisfy: `/var/tmp` not implemented as stand-alone filesystem.

Typically, STIG guidance recommends not that `/var/tmp` be a truly standalone filesystem but as a bind-mount of `/var/tmp`. When so implemented, `/var/tmp` inherits the same mount-options used for `/tmp`. Industry best-practices around the implementation of `/tmp` and `/var/tmp` is that the former is ephemeral — contents disappear at each boot and/or by way of a "`/tmp` cleaner" process &dash; while the contents of `/var/tmp` are non-ephemeral. Further, most Enterprise Linux users expect the contents of `/var/tmp` to be non-ephemeral. Because `/tmp` is a VMS-based pseudo-filesystem, the only way to meet both the industry best-practices guidance and user assumptions for `/var/tmp` is to _not_ make `/var/tmp` a bind-mount of `/tmp`. Because the STIGs fail to specify "`/var` must be a standalone filesystem" and not wishing to waste further disk-space to create a `/var/tmp` separate from the `/var` filesystem, `/var/tmp` is typically left as a subdirectory of the `/var` filesystem. This means that `/var/tmp` has no mount options of its own. The only appicable mount options are those inherited from the parent `/var` filesystem.

Note: for programs that place the additional requirement that `/var/tmp` _must_ be a standalone filesystem, it is recommended to up the size of the root volume-group, create an LVM volume to host the `/var/tmp` filesystem and then apply the site-local mount-options to the filesystem. This can all be accomplished at system provisioning-time, but is outside the scope of the watchmaker utility to effect.

### `/var/tmp` — `nosuid` Option Missing

Cannot satisfy: `/var/tmp` not implemented as stand-alone filesystem.

Typically, STIG guidance recommends not that `/var/tmp` be a truly standalone filesystem but as a bind-mount of `/var/tmp`. When so implemented, `/var/tmp` inherits the same mount-options used for `/tmp`. Industry best-practices around the implementation of `/tmp` and `/var/tmp` is that the former is ephemeral — contents disappear at each boot and/or by way of a "`/tmp` cleaner" process &dash; while the contents of `/var/tmp` are non-ephemeral. Further, most Enterprise Linux users expect the contents of `/var/tmp` to be non-ephemeral. Because `/tmp` is a VMS-based pseudo-filesystem, the only way to meet both the industry best-practices guidance and user assumptions for `/var/tmp` is to _not_ make `/var/tmp` a bind-mount of `/tmp`. Because the STIGs fail to specify "`/var` must be a standalone filesystem" and not wishing to waste further disk-space to create a `/var/tmp` separate from the `/var` filesystem, `/var/tmp` is typically left as a subdirectory of the `/var` filesystem. This means that `/var/tmp` has no mount options of its own. The only appicable mount options are those inherited from the parent `/var` filesystem.

Note: for programs that place the additional requirement that `/var/tmp` _must_ be a standalone filesystem, it is recommended to up the size of the root volume-group, create an LVM volume to host the `/var/tmp` filesystem and then apply the site-local mount-options to the filesystem. This can all be accomplished at system provisioning-time, but is outside the scope of the watchmaker utility to effect.

## Missing Audit Rules

Some third-paty scanners will incorrectly indicate that the `auditd` subsystem is missing rules.

### Ensure Kernel Module (Un)Loading Information Is Collected

Already implemented in the `/etc/audit/rules.d/modules.rules` and `/etc/audit/audit.rules` files. Watchmaker-applied rule uses `-k` to signify the audit event-key. Complaining scanner-utility is likely searching for the `key=` token to signify the audit event-key or similarly-incompatible search-string.

### Ensure Attempts to Alter Logon and Logout Events Is Collected

Already implemented in the `/etc/audit/audit.rules` and `/etc/audit/rules.d/logins.rules` files. Watchmaker-applied rule uses `-k` to signify the audit event-key. Complaining scanner-utility is likely searching for the `key=` token to signify the audit event-key or similarly-incompatible search-string.

### Ensure Use of Privileged Commands Is Collected

Already implemented in the `/etc/audit/audit.rules` and `/etc/audit/rules.d/privileged.rules` files. Watchmaker-applied rule uses `-k` to signify the audit event-key. Complaining scanner-utility is likely searching for the `key=` token to signify the audit event-key or similarly-incompatible search-string.

## Ensure `/var/tmp` Located On Separate Partition

System (re)partitioning is outside the scope of Watchmaker: altering system's partitioning-scheme is not part of Watchmaker's functionality.

This configuration item is not part of baseline STIGs, thus not typically implemented within standardized builds/templates (see discussions in any of the above _Missing Option for `/var/tmp` Filesystem_ sections).
