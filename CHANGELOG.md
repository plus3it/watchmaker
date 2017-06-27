# Changelog

0.5.0 (2017.06.27)

*   [[Issue #331][331]][[PR #332][332]] Writes the `role` grain to the key
    expected by the ash-windows formula. Fixes usage of the `--ash-role` option
    in the salt worker
*   [[Issue #329][329]][[PR #330][330]] Outputs watchmaker version at the debug
    log level
*   [[Issue #322][322]][[PR #323][323]][[PR #324][324]] Fixes py2/py3
    compatibility bug in how the yum worker handles file opening to check the
    Linux distro
*   [[Issue #316][316]][[PR #320][320]] Improves logging when salt state
    execution fails due to failed a state. The salt output is now returned to
    the salt worker, which processes the output, identifies the failed state,
    and raises an exception with the state failure
*   join-domain-formula
    *   (Linux) Reworks the pbis config states to make the logged output more
        readable

[332]: https://github.com/plus3it/watchmaker/pull/332
[331]: https://github.com/plus3it/watchmaker/issues/331
[330]: https://github.com/plus3it/watchmaker/pull/330
[329]: https://github.com/plus3it/watchmaker/issues/329
[324]: https://github.com/plus3it/watchmaker/pull/324
[323]: https://github.com/plus3it/watchmaker/pull/323
[322]: https://github.com/plus3it/watchmaker/issues/322
[320]: https://github.com/plus3it/watchmaker/pull/320
[316]: https://github.com/plus3it/watchmaker/issues/316

0.4.4 (2017.05.30)

*   join-domain-formula
    *   (Linux) Ignores a bad exit code from pbis config utility. The utility
        will return exit code 5 when modifying the NssEnumerationEnabled
        setting, but still sets the requested value. This exit code is now
        ignored

0.4.3 (2017.05.25)

*   name-computer-formula
    *   (Linux) Uses an alternate method of working around a bad code-path in
        salt that does not handle quoted values in /etc/sysconfig/network.

0.4.2 (2017.05.19)

*   [[PR #301][301]] Sets the grains for admin_groups and admin_users so the
    keys are named as expected by the join-domain formula
*   ash-linux-formula
    *   Adds a custom module that lists users from the shadow file
    *   Gets local users from the shadow file rather than `user.list_users`.
        Prevents a domain-joined system from attempting to iterate over all
        domain users (and potentially deadlocking on especially large domains)
*   join-domain-formula
    *   Modifies PBIS install method to use RPMs directly, rather than the
        SHAR installer
    *   Updates approaches to checking for collisions and current join status
        to better handle various scenarios: not joined, no collision; not
        joined, collision; joined, computer object present; joined, computer
        object missing
    *   Disables NSS enumeration to prevent PBIS from querying user info from
        the domain for every call to getent (or equivalents); domain-based
        user authentication still works fine
*   name-computer-formula
    *   (Linux) Does not attempt to retain network settings, to avoid a bug in
        salt; will be revisited when a patched salt version has been released

[301]: https://github.com/plus3it/watchmaker/pull/301

0.4.1 (2017.05.09)

*   (EL7) Running _watchmaker_ against EL7 systems will now pin the resulting
    configuration to the watchmaker version. See the updates to the two
    formulas in this version. Previously, _ash-linux_ always used the content
    from the `scap-security-guide` rpm, which was updated out-of-sync with
    _watchmaker_, and so the resulting configuration could not be pinned by
    pinning the _watchmaker_ version. With this version, _ash-linux_ uses
    content distributed by _watchmaker_, via _scap-formula_, and so the
    resulting configuration will always be same on EL7 for a given version of
    _watchmaker_ (as has always been the case for the other supported
    operating systems).
*   ash-linux-formula
    *   Supports getting scap content locations from pillar
*   scap-formula
    *   Updates stig content with latest benchmark versions
    *   Adds openscap ds.xml content, used to support remediate actions

0.4.0 (2017.05.06)

*   [[PR #286 ][286]] Sets the computername grain with the correct key expected
    by the formula
*   [[PR #284 ][284]] Converts cli argument parsing from `argparse` to `click`.
    This modifies the `watchmaker` depedencies, which warranted a 0.x.0 version
    bump. Cli and API arguments remain the same, so the change should be
    backwards-compatible.
*   name-computer-formula
    *   Adds support for getting the computername from pillar
    *   Adds support for validating the specified computername against a
        pattern
*   pshelp-formula
    *   Attempts to address occasional stack overflow exception when updating
        powershell help

[286]: https://github.com/plus3it/watchmaker/pull/286
[284]: https://github.com/plus3it/watchmaker/pull/284

0.3.1 (2017.05.01)

*   [[PR #280][280]] Modifies the dynamic import of boto3 to use only absolute
    imports, as the previous approach (attempt absolute and relative import)
    was deprecated in Python 3.3
*   ntp-client-windows-formula:
    *   Stops using deprecated arguments on reg.present states, which cleans up
        extraneous log messages in watchmaker runs under some configurations
*   join-domain-formula:
    *   (Windows) Sets the DNS search suffix when joining the domain, including
        a new pillar config option, `ec2config` to enable/disable the EC2Config
        option that also modifies the DNS suffix list.

[280]: https://github.com/plus3it/watchmaker/pull/280

0.3.0 (2017.04.24)

*   [[Issue #270][270]] Defaults to a platform-specific log directory when
    call from the CLI:
    *   Windows: `${Env:SystemDrive}\Watchmaker\Logs`
    *   Linux: `/var/log/watchmaker`
*   [[PR #271][271]] Modifies CLI arguments to use explicit log-levels rather
    than a verbosity count. Arguments have been adjusted to better accommodate
    the semantics of this approach:
    *   Uses `-l|--log-level` instead of `-v|--verbose`
    *   `-v` and `-V` are now both used for `--version`
    *   `-d` is now used for `--log-dir`

[271]: https://github.com/plus3it/watchmaker/pull/271
[270]: https://github.com/plus3it/watchmaker/issues/270

0.2.4 (2017.04.20)

*   Fixes a bad version string

0.2.3 (2017.04.20)

*   [[Issue #262][262]] Merges lists in pillar files, rather than overwriting
    them
*   [[Issue #261][261]] Manages the enabled/disabled state of the salt-minion
    service, before and after the install
*   splunkforwarder-formula
    *   (Windows) Ignores false bad exits from Splunk clone-prep-clear-config

[262]: https://github.com/plus3it/watchmaker/issues/262
[261]: https://github.com/plus3it/watchmaker/issues/261

0.2.2 (2017.04.15)

*   [[PR #251][251]] Adds CloudFormation templates that integrate Watchmaker
    with an EC2 instance or Autoscale Group
*   join-domain-formula
    *   (Linux) Corrects tests that determine whether the instance is already
        joined to the domain

[251]: https://github.com/plus3it/watchmaker/pull/251

0.2.1 (2017.04.10)

*   ash-linux-formula
    *   Reduces spurious stderr output
    *   Removes notify script flagged by McAfee scans
*   splunkforwarder-formula
    *   (Windows) Clears system name entries from local Splunk config files

0.2.0 (2017.04.06)

*   [[Issue #238][238]] Captures all unhandled exceptions and logs them
*   [[Issue #234][234]] Stops the salt service prior to managing salt formulas,
    to ensure that the filesystem does not throw any errors about the files
    being locked
*   [[Issue #72][72]] Manages salt service so the service state after
    watchmaker completes is the same as it was prior to running watchmaker. If
    the service was running beforehand, it remains running afterwards. If the
    service was stopped (or non-existent) beforehad, the service remains
    stopped afterwards
*   [[Issue #163][163]] Modifies the `user_formulas` config option to support
    a map of `<formula_name>:<formula_url>`
*   [[PR #235][235]] Extracts salt content to the same target `srv` location
    for both Window and Linux. Previously, the salt content was extracted to
    different points in the filesystem hierarchy, which required different
    content for Windows and Linux. Now the same salt content archive can be
    used for both
*   [[PR #242][242]] Renames salt worker param `content_source` to
    `salt_content`
*   systemprep-formula
    *   Deprecated and removed. Replaced by new salt content structure that
        uses native salt capabilities to map states to a system
*   scc-formula
    *   Deprecated and removed. Replaced by scap-formula
*   scap-formula
    *   New bundled salt formula. Provides SCAP scans using either `openscap`
        or `scc`
*   pshelp-formula
    *   New bundled salt formula. Installs updated PowerShell help content to
        Windows systems

[242]: https://github.com/plus3it/watchmaker/pull/242
[235]: https://github.com/plus3it/watchmaker/pull/235
[163]: https://github.com/plus3it/watchmaker/issues/163
[72]: https://github.com/plus3it/watchmaker/issues/72
[234]: https://github.com/plus3it/watchmaker/issues/234
[238]: https://github.com/plus3it/watchmaker/issues/238

0.1.7 (2017.03.23)

*   Uses threads to stream stdout and stderr to the watchmaker log when
    executing a command via subproces
*   [[Issue #226][226]] Minimizes salt output of successful states, to
    make it easier to identify failed states
*   join-domain-formula
    *   (Linux) Exits with stateful failure on a bad decryption error
*   mcafee-agent-formula
    *   (Linux) Avoids attempting to diff a binary file
    *   (Linux) Installs `ed` as a dependency of the McAfee VSEL agent
*   scc-formula
    *   Retries scan up to 5 times if scc exits with an error

[226]: https://github.com/plus3it/watchmaker/issues/226

0.1.6 (2017.03.16)

*   ash-linux-formula
    *   Provides same baseline states for both EL6 and EL7

0.1.5 (2017.03.15)

*   ash-linux-formula
    *   Adds policies to disable insecure Ciphers and MACs in sshd_config
*   ash-windows-formula
    *   Adds `scm` and `stig` baselines for Windows 10
    *   Adds `scm` baseline for Windows Server 2016 (Alpha)
    *   Updates all `scm` and `stig` baselines with latest content
*   mcafee-agent-formula
    *   Uses firewalld on EL7 rather than iptables
*   scc-formula
    *   Skips verification of GPG key when install SCC RPM
*   splunkforwarder-formula
    *   Uses firewalld on EL7 rather than iptables

0.1.4 (2017.03.09)

*   [[Issue #180][180]] Fixes bug where file_roots did not contain formula paths

[180]: https://github.com/plus3it/watchmaker/issues/180

0.1.3 (2017.03.08)

*   [[Issue #164][164]] Aligns cli syntax for extra_arguments with other cli opts
*   [[Issue #165][165]] Removes ash_role from default config file
*   [[Issue #173][173]] Fixes exception when re-running watchmaker

[173]: https://github.com/plus3it/watchmaker/issues/173
[164]: https://github.com/plus3it/watchmaker/issues/164
[165]: https://github.com/plus3it/watchmaker/issues/165

0.1.2 (2017.03.07)

*   Adds a FAQ page to the docs
*   Moves salt formulas to the correct location on the local filesystem
*   join-domain-formula:
    *   (Linux) Modifies decryption routine for FIPS compliance
*   ash-linux-formula:
    *   Removes several error exits in favor of warnings
    *   (EL7-alpha) Various patches to improve support for EL7
*   dotnet4-formula:
    *   Adds support for .NET 4.6.2
    *   Adds support for Windows Server 2016
*   emet-formula:
    *   Adds support for EMET 5.52

0.1.1 (2017.02.28)

*   Adds more logging messages when downloading files

0.1.0 (2017.02.22)

*   Initial release!
