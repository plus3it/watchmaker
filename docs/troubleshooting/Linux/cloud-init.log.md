```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# The `/var/log/cloud-init.log` Log-File

This is the default location where the Red Hat packaged version of the `cloud-init` service for Enterprise Linux 6 and 7 writes _all_ of its log-output to &ndash; on RHEL 8+, logging data is split-out across this file and the `/var/log/cloud-init-output.log` file. All automation directly-initiated through `cloud-init` and that emits STDOUT and/or STDERR messages will be duplicated here. 

Primary diagnostic-use with respect to execution of `watchmaker` will be in tracking errors emitted during _preparation to execute_ `watchmaker`. If the `watchmaker` process fails to start (meaning that `/var/log/watchmaker/watchmaker.log` is never created), this would be a good location to find _why_ `watchmaker` failed to start.

Useful string-searches for locating executional points-of-interest ("landmarks") will be (ordered most- to least-useful):

* `: FAIL: `
* `/var/lib/cloud/instance/script`
* `/var/lib/cloud/instance`
* `: SUCCESS: `

By far, the search for `: FAIL:` will be the most important in uncovering errors. The other searches will mostly be of use in progress-tracking and verifying expected event-sequencing[^1].

## Example Failure

Typically, searching for "`: FAIL:` will bring the file-cursor to a logged-block similar to:

~~~bash
2023-06-21 11:12:36,078 - subp.py[DEBUG]: Unexpected error while running command.
Command: ['/var/lib/cloud/instance/scripts/00_script.sh']
Exit code: 1
Reason: -
Stdout: -
Stderr: -
2023-06-21 11:12:36,078 - cc_scripts_user.py[WARNING]: Failed to run module scripts-user (scripts in /var/lib/cloud/instance/scripts)
2023-06-21 11:12:36,078 - handlers.py[DEBUG]: finish: modules-final/config-scripts-user: FAIL: running config-scripts-user with frequency once-per-instance
2023-06-21 11:12:36,078 - util.py[WARNING]: Running module scripts-user (<module 'cloudinit.config.cc_scripts_user' from '/usr/lib/python3.6/site-packages/cloudinit/config/cc_scripts_user.py'>) failed
2023-06-21 11:12:36,079 - util.py[DEBUG]: Running module scripts-user (<module 'cloudinit.config.cc_scripts_user' from '/usr/lib/python3.6/site-packages/cloudinit/config/cc_scripts_user.py'>) failed
Traceback (most recent call last):
  File "/usr/lib/python3.6/site-packages/cloudinit/stages.py", line 1090, in _run_modules
    run_name, mod.handle, func_args, freq=freq
  File "/usr/lib/python3.6/site-packages/cloudinit/cloud.py", line 55, in run
    return self._runners.run(name, functor, args, freq, clear_on_fail)
  File "/usr/lib/python3.6/site-packages/cloudinit/helpers.py", line 185, in run
    results = functor(*args)
  File "/usr/lib/python3.6/site-packages/cloudinit/config/cc_scripts_user.py", line 44, in handle
    subp.runparts(runparts_path)
  File "/usr/lib/python3.6/site-packages/cloudinit/subp.py", line 426, in runparts
    % (len(failed), ",".join(failed), len(attempted))
RuntimeError: Runparts: 1 failures (00_script.sh) in 1 attempted commands
~~~

In this case, the failure happened during the execution of the userdata-script, `/var/lib/cloud/instance/scripts/00_script.sh`. Even if the script hasn't logged anything directly useful in this log file or hasn't even been configured to log its own activities any where, knowing that it was during the execution of this file is useful.

1. The provisioning-administrator knows where in the `cloud-init` automation-sequence things failed
2. One can look in other logs for actionable diagnostic-information
3. If there's no such information in other log files, one can hand-execute the failing script to see if the error can be reproduced (and in a way that assists the provisioning-administator with isolating the source of the failure)

For the third point, if the failure is in a BASH script, executing the script with the diagnostic flag set (e.g., `bash -x /var/lib/cloud/instance/scripts/00_script.sh`) one may be able to see where the script fails.

Similarly, if hand-execution of the script _succeeds_ it can point to the script making incorrect assumptions about the `cloud-init` managed execution environment. This can include things like:

- Lack of necessary environment variables
- Improperly defined environment-variables
- Attempts to execute commands that require a controlling-TTY (i.e., an interactive-login shell)
- Attempting to do something that the instance's security posture blocks[^2].

Note that comparing execution via `cloud-init` versus execution from an interactive-shell works whether the script is written in BASH or some other interpreted language.

[^1]: Event-sequencing issues most-frequently happen when a userData payload delivers two or more scripts. When multiple scripts are specified in a userData payload, they are not necessarily executed in the same order they're specified in the userData text-stream. Instead, `cloud-init` executes scripts placed into the `/var/lib/cloud/instance/scripts/` directory in alphabetical order. Thus, if one _needs_ the scripts to execute in a specific order, it is important to carefully name them such that that happens (e.g., `00_script` and `01_script` would result in the `00_`-prefixed script executing prior the `01_`-prefixed script)
[^2]: SELinux can be especially problematic for processes started by `cloud-init`. For example, the `firewall-cmd` utility is not directly usable. `cloud-init` scripts would need to either issue a `setenforce 0` before invoking the command or use the alternate `firewall-offline-command`
