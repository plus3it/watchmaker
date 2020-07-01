[![License](https://img.shields.io/github/license/plus3it/watchmaker.svg)](./LICENSE)
[![Travis CI Build Status](https://travis-ci.org/plus3it/watchmaker.svg?branch=develop)](https://travis-ci.org/plus3it/watchmaker)
[![Azure DevOps Build Status](https://dev.azure.com/plus3it/watchmaker/_apis/build/status/plus3it.watchmaker?branchName=develop)](https://dev.azure.com/plus3it/watchmaker/_build/latest?definitionId=1&branchName=develop)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/plus3it/watchmaker?branch=develop&svg=true)](https://ci.appveyor.com/project/plus3it/watchmaker)
[![Latest Version](https://img.shields.io/pypi/v/watchmaker.svg?label=version)](https://pypi.python.org/pypi/watchmaker)
[![pullreminders](https://pullreminders.com/badge.svg)](https://pullreminders.com?ref=badge)

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
<https://watchmaker.cloudarmor.io>.
