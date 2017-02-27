[![License](https://img.shields.io/github/license/plus3it/watchmaker.svg)](./LICENSE)
[![Travis CI Build Status](https://travis-ci.org/plus3it/watchmaker.svg?branch=develop)](https://travis-ci.org/plus3it/watchmaker)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/plus3it/watchmaker?branch=develop&svg=true)](https://ci.appveyor.com/project/plus3it/watchmaker)

# Watchmaker

Applied Configuration Management

## Overview

Watchmaker is a Python package that helps bootstrap a vanilla OS image and
apply an OS configuration. Watchmaker itself reads a simple YAML configuration
file, which can be hosted on the local filesystem or on a web server.

Complex configuration management (CM) environments may be layered in as part of
the provisioning framework. Watchmaker includes a default configuration that
will install Salt and a handful Salt Formulas that can be used to harden a
system to DISA STIG standards, as well as integrate with common enterprise
services.

## Documentation

For more information on installing and using Watchmaker, go to
<https://watchmaker.readthedocs.io>.

Alternatively, you can build the docs locally using `mkdocs`. From the root of
the project directory, run:

```shell
pip install mkdocs
mkdocs serve
```

This will start a light-weight web server on `http://127.0.0.1:8000` containing
the doc pages for Watchmaker. Also, if you edit the source in the `docs`
directory, the web server will update the page dynamically.
