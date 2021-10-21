```{eval-rst}
.. image:: images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Installation

## From Python Package Index

The preferred method to install `watchmaker` is from the Python Package Index
(PyPi), using [pip][0]. Without any other options, this will always install
the most recent stable release.

```bash
python3 -m pip install watchmaker
```

If you do not have Python or [pip][0], this [Python installation guide][1]
can guide you through the process.

```{eval-rst}
.. note::

    Versions 10 and later of ``pip`` do not support Python 2.6. On CentOS 6 and
    RHEL 6, Python 2.6 is the system version of Python. If you are using Python
    2.6 with ``watchmaker``, you will need to restrict the ``pip`` install such
    that a version earlier than 10 is installed. See the relevant question in
    the [FAQ](faq.html) for more details.
```

## From source

Watchmaker can also be built and installed from source, using `git` and `pip`.
The source for `watchmaker` are available from the [GitHub repo][2].

1.  First clone the public repository to pull the code to your local machine:

    ```bash
    git clone https://github.com/plus3it/watchmaker.git --recursive && cd watchmaker
    ```

    This project uses submodules, so it's easiest to use the `--recursive`
    flag, as above. If you don't, you will need to pull in the submodules as
    well:

    ```bash
    git submodule update --init --recursive
    ```

2.  If you want to install a specific branch or tag, check it out before
    installing Watchmaker:

    ```bash
    git checkout <branch-tag-foo>
    ```

3.  Then you can install Watchmaker:

    ```bash
    python3 -m pip install .
    ```

## From standalone executable

Watchmaker can also be downloaded and executed in an all-in-one package containing
Watchmaker's dependencies, such as Python and necessary Python packages. Packages
are available for Windows and Linux.

1.  Retrieve the Watchmaker standalone package for your desired platform from
    GitHub Releases or the [Cloudarmor repo][5].

    *   [GitHub Releases][3] shows the available Watchmaker versions and includes
        links to the Windows and Linux packages, and their SHA256 hashes.
    *   The [latest release][4] can also be directly accessed on GitHub:

        *   `https://github.com/plus3it/watchmaker/releases/latest/`

    *   The [Cloudarmor repo][5] also contains versioned Watchmaker packages
        and corresponding SHA256 hashes. You can [browse the repo][5], or construct
        the URL to the files using these patterns:

        *   `https://watchmaker.cloudarmor.io/releases/${VERSION}/watchmaker-${VERSION}-standalone-linux-x86_64`
        *   `https://watchmaker.cloudarmor.io/releases/${VERSION}/watchmaker-${VERSION}-sha256-linux-x86_64.json`
        *   `https://watchmaker.cloudarmor.io/releases/${VERSION}/watchmaker-${VERSION}-standalone-windows-amd64.exe`
        *   `https://watchmaker.cloudarmor.io/releases/${VERSION}/watchmaker-${VERSION}-sha256-windows-amd64.json`

    *   The [latest release][6] is always available on the Cloudarmor repo at these
        URLs:

        *   `https://watchmaker.cloudarmor.io/releases/latest/watchmaker-latest-standalone-linux-x86_64`
        *   `https://watchmaker.cloudarmor.io/releases/latest/watchmaker-latest-sha256-linux-x86_64.json`
        *   `https://watchmaker.cloudarmor.io/releases/latest/watchmaker-latest-standalone-windows-amd64.exe`
        *   `https://watchmaker.cloudarmor.io/releases/latest/watchmaker-latest-sha256-windows-amd64.json`

    *   From PowerShell, the Windows package can be downloaded as follows:

        ```ps1con
        PS C:\wam> $url = "https://watchmaker.cloudarmor.io/releases/latest/watchmaker-latest-standalone-windows-amd64.exe"
        PS C:\wam> (New-Object System.Net.WebClient).DownloadFile($url, "watchmaker.exe")
        ```

    *   From the command line, the Linux package can be downloaded as follows:

        ```console
        # curl -so watchmaker https://watchmaker.cloudarmor.io/releases/latest/watchmaker-latest-standalone-linux-x86_64
        ```

    *   For the latest package, the version of Watchmaker can be determined by
        viewing the contents of the SHA256 hash file or by executing the package
        with the `--version` flag.

2.  Verify the integrity of the standalone package.

    Compare the SHA256 hash contained in the downloaded hash file to a hash you
    compute for the package.

    For Linux, execute this command to compute the SHA256 hash:

    ```console
    # shasum -a 256 watchmaker-latest-standalone-linux-x86_64
    ```

    For Windows, execute this command to compute the SHA256 hash:

    ```ps1con
    PS C:\wam> Get-FileHash watchmaker-latest-standalone-windows-amd64.exe | Format-List
    ```

3.  Set executable access permission.

    For Linux, you will need to set the access permissions to allow the standalone
    executable to run. Below is an example:

    ```console
    # chmod +x watchmaker-latest-standalone-linux-x86_64
    ```


[0]: https://pip.pypa.io/en/stable/
[1]: https://python-guide.readthedocs.io/en/latest/starting/installation/
[2]: https://github.com/plus3it/watchmaker
[3]: https://github.com/plus3it/watchmaker/releases/
[4]: https://github.com/plus3it/watchmaker/releases/latest/
[5]: https://watchmaker.cloudarmor.io/list.html
[6]: https://watchmaker.cloudarmor.io/list.html#releases/latest/
