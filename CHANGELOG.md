# Changelog

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
