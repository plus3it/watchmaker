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

  +-------------------------------------------------------------------------------------+---------------------+
  | Finding Summary                                                                     | Finding Identifiers |
  +=====================================================================================+=====================+
  | `Prevent System Daemons From Using Kerberos For Authentication`_                    | V-230238            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-010161      |
  +-------------------------------------------------------------------------------------+---------------------+
  | `Users Must Provide A Password For Privilege Escalation`_                           | V-230271            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-010380      |
  +-------------------------------------------------------------------------------------+---------------------+
  | `A Separate Filesystem Must Be Used For the /tmp Directory`_                        | V-230295            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-010543      |
  +-------------------------------------------------------------------------------------+---------------------+
  | `The OS must mount /tmp with the nodev option`_                                     | V-230511            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-040123      |
  +-------------------------------------------------------------------------------------+---------------------+
  | `The OS must mount /tmp with the nosuid option`_                                    | V-230512            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-040124      |
  +-------------------------------------------------------------------------------------+---------------------+
  | `The OS must mount /tmp with the noexec option`_                                    | V-230514            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-040125      |
  +-------------------------------------------------------------------------------------+---------------------+
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

As with the "<i><a href="#the-os-must-mount-`/tmp`-with-the-nodev-option">The OS must mount `/tmp` with the nodev option</a></i>" finding, this finding is due to an incompatibility between how the scanner checks for the setting and how the setting is actually implemented.

**Proof of Correctness:**

To validate that the required-setting is _actually_ present, execute:

~~~
grep -w /tmp /proc/mounts | grep nosuid
~~~

If this returns null, the scan-result is valid; otherwise the scan-result is _invalid_.

# The OS must mount `/tmp` with the `noexec` option

As with the "<i><a href="#the-os-must-mount-`/tmp`-with-the-nodev-option">The OS must mount `/tmp` with the nodev option</a></i>" finding, this finding is due to an incompatibility between how the scanner checks for the setting and how the setting is actually implemented.

**Proof of Correctness:**

To validate that the required-setting is _actually_ present, execute:

~~~
grep -w /tmp /proc/mounts | grep noexec
~~~

If this returns null, the scan-result is valid; otherwise the scan-result is _invalid_.
