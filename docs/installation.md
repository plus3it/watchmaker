# Installation

## Stable release

To install `watchmaker`, run this command in your terminal:

```bash
pip install watchmaker
```

This is the preferred method to install `watchmaker`, as it
will always install the most recent stable release.

If you do not have [`pip`][0] installed, this [Python installation guide][1]
can guide you through the process.

## From sources

The sources for `watchmaker` can be downloaded from the [`GitHub repo`][2].

First clone the public repository:

```bash
git clone https://github.com/plus3it/watchmaker.git && cd watchmaker
```

This project uses submodules, so once you have a copy of the source, you need
to pull them in as well.

```bash
git submodule update --init --recursive
```

Then you can install Watchmaker:

```bash
pip install .
```

[0]: https://pip.pypa.io/en/stable/
[1]: https://python-guide.readthedocs.io/en/latest/starting/installation/
[2]: https://github.com/plus3it/watchmaker
