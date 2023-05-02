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
