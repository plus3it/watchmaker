```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# X11-Forwarding Via SSH is "Broken" (EL8)

The STIG-handlers for:

* RHEL-08-040340 (and its Oracle equivalent, OL08-00-040340): 
    > _RHEL 8 remote X connections for interactive users must be disabled unless to fulfill documented and validated mission requirements._
* RHEL-08-020041 (and its Oracle equivalent, OL08-00-020041):
    > _RHEL 8 must ensure session control is automatically started at shell initialization_

These settings will negatively-impact expected behaviors around X11-forwarding through SSH tunnels after application.

## Symptoms

An error like "Can't open display" is emitted when attempting to launch X11 client-applications

## Things to Verify

* Is `X11Forwarding` disabled in the `/etc/ssh/sshd_config` file
* Is the `xauth` utility available: this utility is installed at `/usr/bin/xauth` through the installation of the `xorg-x11-xauth` RPM
* Was X11-forwarding requested by the SSH client when establishing the connection to the remote host

## Fixes

### `X11Forwarding` is disabled in the `/etc/ssh/sshd_config` file

Do the following to allow the use of X11-forwarding over SSH:

1. Execute `sudo grep -P '^(\s*)X11' /etc/ssh/sshd_config`. If the previous command returns null or shows a value of `no`
1. Update the `/etc/ssh/sshd_config` file to:
    * Ensure that any (uncommented) value for `X11Forwarding` is set to `yes`
    * Add a `X11Forwarding yes` line to the file if no uncommented `X11Forwarding` lines exist
1. Restart the `sshd` service

```{eval-rst}
.. note::

    The preceding will result in a scan-finding on any system that it has been
    executed on. The "&hellip;unless to fulfill documented and validated mission
    requirements" component of the STIG-rule means that provision of a
    documented reason for the enablement should allow the finding to be
    dismissed.
```

### No `xauth` utility available

* Ensure that the `xorg-x11-xauth` RPM is installed
* Ensure that `/usr/bin` is in the user's `PATH` environment

### Ensure that X11 forwarding has been requested by your SSH client

The methods for requesting X11 forwarding are specific to each SSH client. OpenSSH clients typically require including the `-Y` flag when requesting a connection. Consult vendor-documents for the proper setup of other SSH clients.

## Next Steps

Assuming that all of the above verifications and associated fixes have been done and things still are not working as expected, it's likely that, when the login processes start up the `tmux` service, that the (tunneled) `DISPLAY` environment variable has not been properly set. This may occur because, when the `tmux` service is activated, the `DISPLAY` variable was not propagated from the initial login-shell to the `tmux`-managed subshell(s). If all other necessary components for setting up X-over-SSH are in place, the following should allow the session-user to set up an appropriate `DISPLAY` value within their `tmux` session-window:

1. Verify that your `${HOME}/.Xauthority` file exists
2. List out the authorization entries in the authority-file (execute `xauth list`). This should result in output like:
    ```
    x-test.wam.lab/unix:10  MIT-MAGIC-COOKIE-1  dbb1c620b838faf7d5e5717d4a217a7c
    ```
    On a freshly-launched system, there should be one and only one entry. If there's more than one entry, it means that either the file is stale or that more than one login-session has been concurrently opened to the remote host
3. Export the environment variable `DISPLAY`, setting it to `localhost:<NUMBER>`. The value of `<NUMBER>` will be the digit after the `<hostname>/unix:` string in the `xauth list` output. Typically, this will mean executing `export DISPLAY=localhost:10`.

Once the above has been done, attempts to launch X11 clients _should_ result in them displaying to the display of the system the operator has originally SSHed from.

```{eval-rst}
.. note::

    If one takes advantage of ``tmux``'s ability to multiplex terminal and one
    wishes to be able to launch X11 apps from any ``tmux``-managed session-window,
    it will be necessary to export the ``DISPLAY`` variable in *each* ``tmux``
    session-window.
```
