```{eval-rst}
.. image:: ../../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# The `/var/log/watchmaker/salt_call.debug.log` Log-File

This is the log-file that captures the bulk of the SaltStack-related state-output. This file gets created when `watchmaker` has been able to successfully download all of its execution information. This file gets created shortly after this line appears in the `/var/log/watchmaker/watchmaker.log` file:

~~~
2023-06-15 11:13:27,378 [watchmaker.workers.base.SaltLinux][DEBUG][6407]: Command: /usr/bin/salt-call --local --retcode-passthrough --no-color --config-dir /opt/watchmaker/salt --log-file /var/log/watchmaker/salt_call.debug.log --log-file-level debug --log-level error --out quiet --return local state.highstate
~~~

Typically, the only errors that will appear here are the results of errors in the SaltStack formulae for the standard integrations. To see which modules _may_ get logged into this file, look at the contents of the `/srv/watchmaker/salt/formulas/` directory and then cross-reference those directories against the contents of the `/srv/watchmaker/salt/states/top.sls` file. To help interpret, a typical `top.sls` file's contents is offered:

~~~

{%- set environments = ['dev', 'test', 'prod', 'dx'] %}

base:
  'G@os_family:RedHat':
    - name-computer
    - scap.content
    - ash-linux.vendor
    - ash-linux.stig
    - ash-linux.iavm
{%- if salt.grains.get('watchmaker:enterprise_environment') | lower in environments %}
    - join-domain
    - mcafee-agent
    - splunkforwarder
    - nessus-agent.elx.install
    # Recommend other custom states be inserted here
{%- endif %}
    - scap.scan

  'G@os_family:Windows':
    [...elided...]
~~~

In the above, these salt formulas will be executed unconditionally on RedHat-derivative systems:

- `/srv/watchmaker/salt/formulas/name-computer-formula`
- `/srv/watchmaker/salt/formulas/ash-linux-formula`[^1]

Similarly, the contents of the following directories will be executed by `watchmaker` only if the environment specified in the `watchmaker`-invocation (the string-value after the `-e` flag) matches one of the elements in the `environments` list.

- `/srv/watchmaker/salt/formulas/join-domain-formula`
- `/srv/watchmaker/salt/formulas/mcafee-agent-formula`
- `/srv/watchmaker/salt/formulas/nessus-agent-formula`
- `/srv/watchmaker/salt/formulas/splunkforwarder-formula`

Similarly, the behavior of each of the above states' executions will be governed by content specified under the `/srv/watchmaker/salt/pillar` directory hierarchy. This content is used to feed values into the parameter-driven SaltStack states enumerated in the `.../formulas` directories.

## Typical Error Causes

The most frequent causes of errors, once `watchmaker` has caused `Saltstack` states to begin their execution, are errors encountered while running the individual enterprise-integration states. Typically, these errors are around stale configuration data (expired domain-join credentials for directory-integration or stale host/IP/port information for other services) or communication-issues between the OS that `watchmaker` is configuring and the service `watchmaker` is attempting to configure the instance to integrate: DNS resolution, host or network-level firewall rules, other transit-issues.

The next most frequent errors are already-existing configuration problems in the OS that `watchmaker` is configuring. These include things like:
- Failures accessing RPM repositories (especially problematic with repositories that require client-cert authentication where there are certificate-expiration problems between the RPM client and repository server)
- Too little storage in critical partitions
- The `watchmaker` activities running after something else has changed a resource-configuration that `watchmaker` expects to manage but finds the resource in an unanticipated state

The least frequent cause of errors is related to the SaltStack code itself. Usually, this is caught in pre-release testing, but "bugs happen". While states are typically coded to try to gracefully handle errors encountered &ndash; they'll typically still fail, but at least try to provide meaningful error-output. Usually, the "bugs happen" errors are resultant of environment-to-environment deltas that were not adequately specified to the code-maintainers or the requisite logic-branching was not able to be adequately exercised across the various environments.

For errors in enterprise-integration content, efforts have been undertaken to try to ensure those errors are adequately represented in this log-file. However, the application-specific logs (the ones _for_ the integrated-application) will still remain the authoritative source for troubleshooting exercises.

[^1]: Due to the `ash-linux.vendor`, `ash-linux.stig` and `ash-linux.iavm` specification, only the `ash-linux-formula`'s `vendor`, `stig` and `iavm` states' executions will be attempted.

