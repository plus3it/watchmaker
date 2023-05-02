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

  +-------------------------------------------------------------------------------------+---------------------+
  | Finding Summary                                                                     | Finding Identifiers |
  +=====================================================================================+=====================+
  | `Prevent System Daemons From Using Kerberos For Authentication`_                    | V-230238            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-010161      |
  +-------------------------------------------------------------------------------------+---------------------+
  | `Users Must Provide A Password For Privilege Escalation`_                           | V-230271            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-01038       |
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
