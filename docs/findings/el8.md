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

  +-------------------------------------------------------------------------------------+---------------------+
  | Finding Summary                                                                     | Finding Identifiers |
  +=====================================================================================+=====================+
  | `Prevent System Daemons From Using Kerberos For Authentication`_                    | V-230238            |
  |                                                                                     |                     |
  |                                                                                     | RHEL-08-010161      |
  +-------------------------------------------------------------------------------------+---------------------+
```


# Prevent System Daemons From Using Kerberos For Authentication

**Condtionally-valid Finding:**

If an EL8 system is bound to Active Directory &ndash; or other Kerberos-enabled centralized authentication-source &ndash; or is _acting as_ a Kerberos domain controller (KDC), the presence of an `/etc/krb5.keytab` file is mandatory. 

If the scanned system does not have the `krb5-workstation` or `krb5-server` packages installed and _any_ `.keytab` files are found in the `/etc` directory, this is a valid finding.
