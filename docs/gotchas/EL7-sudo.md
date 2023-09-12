```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Use of `sudo` broken after application of "extra" hardenings (EL7)

The STIG-handlers for each of RHEL-07-020020 and RHEL-07-020023 can break ability to `sudo` if applied. 


```{eval-rst}
.. note::

    1. These hardenings have, historically, not been universally applied to watchmaker-hardened systems. However, they are included with the hardening contents and some watchmaker-users do choose to execute them.
    2. Use with more-recent spel AMIs may avoid the problems reported, as those AMIs already include updated SELinux-related sudoers configurations.
```


* RHEL-07-020020

    > **Rule Title:** _The Red Hat Enterprise Linux operating system must prevent non-privileged users from executing privileged functions to include disabling, circumventing, or altering implemented security safeguards/countermeasures._

    This handler for this STIG-ID makes sure that every local user with a `uid` and/or `gid` respectively greater than the `SYS_UID_MAX` and `SYS_GID_MAX` settings in the `/etc/login.defs` file has an SELinux user-confinement defined. These confinements can be viewed by executing:

    ~~~
    semanage login -l
    ~~~

    If a local user hasn't already had a user-confinement applied, this state will apply one. The state will search relevant Pillar-data to look for confinement-mappings and apply any that are defined. The relevant Pillar data is defined in the `/srv/watchmaker/salt/pillar/<ENVIRONMENT>/init.sls` file under the `ash-linux:lookup:sel_confine` map-object.

    One can check if watchmaker is aware of this map-object by typing:

    ~~~
    salt-call -c /opt/watchmaker/salt pillar.get ash-linux:lookup:sel_confine
    ~~~

    As the `root` user. If execution of this command returns only:

    ~~~
    local:
    ~~~

    Then the pillar-data is not present. If pillar-data _is_ present, then it should return a list of SELinux user-confinements and each returned confinement will have a list of one or more usernames. For example:

    ~~~
    # salt-call -c /opt/watchmaker/salt pillar.get ash-linux:lookup:sel_confine
    local:
        |_
          ----------
          staff_u:
              - ec2-user
        |_
          ----------
          unconfined_u:
              - ssm-user
    ~~~

    Each username listed under a confinement will be given that confinement when RHEL-07-020020 is run.

* RHEL-07-020023

    > **Rule Title:** _The Red Hat Enterprise Linux operating system must elevate the SELinux context when an administrator calls the sudo command._

    This handler makes sure that every user of the `sudo` subsystem has an SELinux privilege-transition defined. These transitions aim to make it so that when users execute `sudo`, they don't have to pass any extra command-options to get the correct SELinux profile.

## User Mapped As `user_u`

If the `ash-linux:lookup:sel_confine` map-object does not exist in the Pillar-data, _every_ local user without an existing confinement will get mapped to the `user_u` confinement. This confinement-level will significantly restrict the things that the user-account can do, inclusive of using `sudo`. In the case of `sudo` these restrictions will manifest similarly to:


~~~
$ sudo -i
sudo: PERM_SUDOERS: setresuid(-1, 1, -1): Operation not permitted
sudo: no valid sudoers sources found, quitting
sudo: setresuid() [0, 0, 0] -> [1004, -1, -1]: Operation not permitted
sudo: unable to initialize policy plugin
$
~~~

## User Mapped As `staff_u`

If the previously-discussed pillar-data declares that a given username should be mapped to the `staff_u` user-confinement, execution of `sudo` _may_ result in an error. A quick `sudo -i` will show:

~~~
$ sudo -i
-bash: /root/.bash_profile: Permission denied
~~~

Some further actions might show output similar to the following:

~~~
-bash-4.2# id -Z
staff_u:staff_r:staff_t:s0-s0:c0.c1023

-bash-4.2# ls -al
ls: cannot access .bashrc: Permission denied
ls: cannot access .bash_history: Permission denied
ls: cannot access .tcshrc: Permission denied
ls: cannot access .bash_profile: Permission denied
ls: cannot access .bash_logout: Permission denied
ls: cannot access install.sh: Permission denied
ls: cannot access .cshrc: Permission denied
total 24
dr-xr-x---.  6 root root 4096 Aug 17 14:35 .
dr-xr-xr-x. 19 root root 4096 Aug 17 12:51 ..
-??????????  ? ?    ?       ?            ? .bash_history
-??????????  ? ?    ?       ?            ? .bash_logout
-??????????  ? ?    ?       ?            ? .bash_profile
-??????????  ? ?    ?       ?            ? .bashrc
-??????????  ? ?    ?       ?            ? .cshrc
drwx------.  2 root root 4096 Aug 17 13:22 .ssh
-??????????  ? ?    ?       ?            ? .tcshrc
~~~

The errors are due to the `sudo` action selecting the default `staff_u:staff_r:staff_t:s0-s0:c0.c1023` SELinux rights-mapping.

**Workaround:**

To work around, invoke `sudo` as follows:

~~~
$ sudo -i -r sysadm_r -t sysadm_t
~~~

The user should receive no SELinux errors before the root prompt is displayed, nor should they receive errors from operations like ` ls ${HOME}`. Similarly, if they execute `id -Z`, they should get output similar to:

~~~
# id -Z
staff_u:sysadm_r:sysadm_t:s0-s0:c0.c1023
~~~


## User Mapped As `unconfined_u`

There are a few ways that users get assigned this confinement: the user was explicitly created with that confinement assigned; they login using a third-party authentication-service like Active directory; or the previously-mentioned pillar-data was configured to map them to that confinement. Typically, so-mapped users will not experience any SELinux-related permissions problems. However, if an SELinux role-transition has been defined in the `sudoers` subsystem (as is done when RHEL-07-020023 is run), the user may experience an error like:

~~~
$ sudo -i
sudo: unconfined_u:sysadm_r:sysadm_t:s0-s0:c0.c1023 is not a valid context
~~~

**Workaround:**

To work around, invoke `sudo` as follows:

~~~
$ sudo -i -r unconfined_r -t unconfined_t
~~~
