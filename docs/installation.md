.. image:: images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://plus3it.com
<br>

# Installation

## From Python Package Index

The preferred method to install `watchmaker` is from the Python Package Index
(PyPi), using [pip][0]. Without any other options, this will always install
the most recent stable release.

```bash
pip install watchmaker
```

If you do not have Python or [pip][0], this [Python installation guide][1]
can guide you through the process.

.. note::

    Versions 10 and later of ``pip`` do not support Python 2.6. On CentOS 6 and
    RHEL 6, Python 2.6 is the system version of Python. If you are using Python
    2.6 with ``watchmaker``, you will need to restrict the ``pip`` install such
    that a version earlier than 10 is installed. See the relevant question in
    the [FAQ](faq.html) for more details.

## From sources

Watchmaker can also be built and installed from source, using `git` and `pip`.
The sources for `watchmaker` are available from the [GitHub repo][2].

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
    pip install .
    ```

## From standalone executable package

Watchmaker can also be downloaded and executed in an all-in-one
package containing Watchmaker's dependencies, such as Python and
necessary Python packages.  Packages are available for Windows and
Linux.

1.  Download the standalone package for your desired platform.

    *   The Windows package is called
        `watchmaker-latest-standalone-windows-amd64.exe`. The
        corresponding SHA256 hash is called
        `watchmaker-latest-sha256-windows-amd64.json`.

        From PowerShell, the Windows package can be downloaded
        as follows:

        ```powershell
        PS C:\wam> $url = "https://s3.amazonaws.com/watchmaker/releases/latest/watchmaker-latest-standalone-windows-amd64.exe"
        PS C:\wam> (New-Object System.Net.WebClient).DownloadFile($url, "watchmaker-latest-standalone-windows-amd64.exe")
        ```

    *   The Linux package is called
        `watchmaker-latest-standalone-linux-x86_64`. The
        corresponding SHA256 hash is called
        `watchmaker-latest-sha256-linux-x86_64.json`.

        From the command line, the Linux package can be downloaded
        as follows:

        ```shell
        # curl -sO https://s3.amazonaws.com/watchmaker/releases/latest/watchmaker-latest-standalone-linux-x86_64
        ```

    *   Watchmaker's [GitHub Releases][3] page includes links to the
        Windows and Linux packages, and SHA256 hashes.
    *   The packages and SHA256 hashes are also available in 
        Watchmaker's [S3 bucket][4].
    *   The version of Watchmaker can be determined by viewing the
        contents of the SHA256 hash file or by executing the package
        with the `--version` flag.

2.  Verify the integrity of the standalone package.

    Compare the SHA256 hash contained in the downloaded hash file to
    a hash you compute for the package.

    For Linux, execute this command to compute the SHA256 hash:
      
    ```shell
    # shasum -a 256 watchmaker-latest-standalone-linux-x86_64
    ```

    For Windows, execute this command to compute the SHA256 hash:

    ```powershell
    PS C:\wam> Get-FileHash watchmaker-latest-standalone-windows-amd64.exe | Format-List
    ```

3.  Set executable access permission.

    For Linux, you will need to set the access permissions to allow the
    standalone executable to run. Below is an example:
    
    ```shell
    # chmod +x watchmaker-latest-standalone-linux-x86_64
    ```


[0]: https://pip.pypa.io/en/stable/
[1]: https://python-guide.readthedocs.io/en/latest/starting/installation/
[2]: https://github.com/plus3it/watchmaker
[3]: https://github.com/plus3it/watchmaker/releases/latest
[4]: https://s3.console.aws.amazon.com/s3/buckets/watchmaker/releases/latest/