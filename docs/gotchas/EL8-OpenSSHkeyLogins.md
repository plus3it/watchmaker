```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# OpenSSH RSAv2 Keys Don't Work (EL8)

## Background

The OpenSSH Daemon shipped with the most-recent versions of RHEL 8 (and derivatives), implements the deprecation of SHA1-signed SSH keys for key-based authentication that's now part of OpenSSH 8.8 and higher. As such, any SSH keys used for key-based authentication will need to be signed using a SHA2 algorithm (SHA-256 or SHA-512).

## Workarounds

For users of self-managed keys, this means that one needs to present an SHA-256 or SHA-512 signed OpenSSH key when using RSAv2 keys for key-based logins. Such keys can be generated in a couple ways:

* Use either `rsa-sha2-256` or `rsa-sha2-512` when using `ssh-keygen`'s `-t` option for generating a new key
* Use `ssh-keygen` on a FIPS-enabled, EL8+ operating system
* Use a CSP's key-generation tool (AWS's commercial region's EC2 key-generation capability is known to create conformant RSAv2 keys)

For users of organizationally-issued SSH keys - be they bare files or as delivered via a centrally-managed SmartCard (such as a PIV or CAC) or other token - it will be necessary for the key-user to work with their organization to ensure that updated, conformant keys are issued.

## Symptoms

Depending on the SSH client, the key may silently fail to work or it may print an error. If an error is printed, it will usually be something like:

```bash
Load key "/path/to/key-file": error in libcrypto
```

With or without the printing of the error, the key will be disqualified and the server will request the client move on to the next-available authentication-metho (usually password).

_If_ one is able to use other means to access a system and view its logs, one will usually find errors similar to:

```bash
Feb 09 12:10:50 ip-0a00dc73 sshd[2939]: input_userauth_request: invalid user ec2-user [preauth]
```

Or

```bash
Feb 09 12:10:50 ip-0a00dc73 sshd[2939]: input_userauth_pubkey: key type ssh-rsa not in PubkeyAcceptedKeyTypes [preauth]
```

In the `/var/log/secure` logs.



**Note:** The deprecated SHA-1 issuse is not a watchmaker issue. It is generically applicable to Red Hat's OpenSSH version on EL8-bsed systems. However, because most people will encounter the issue after having run watchmaker, we opted to include it in this project's "Gotchas" documentation for the benefit of watchmaker-users that might come here for answers
