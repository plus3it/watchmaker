# Installation

## From Python Package Index

The preferred method to install `watchmaker` is from the Python Package Index
(PyPi), using [`pip`][0]. Without any other options, this will always install
the most recent stable release.

```bash
pip install watchmaker
```

If you do not have Python or [`pip`][0], this [Python installation guide][1]
can guide you through the process.

## From sources

Watchmaker can also be built and installed from source, using `git` and `pip`.
The sources for `watchmaker` are available from the [`GitHub repo`][2].

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
    installing watchmaker:

    ```bash
    git checkout <branch-tag-foo>
    ```

3.  Then you can install Watchmaker:

    ```bash
    pip install .
    ```

[0]: https://pip.pypa.io/en/stable/
[1]: https://python-guide.readthedocs.io/en/latest/starting/installation/
[2]: https://github.com/plus3it/watchmaker
