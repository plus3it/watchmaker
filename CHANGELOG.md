# Changelog

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
