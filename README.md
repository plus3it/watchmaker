[![License](https://img.shields.io/github/license/plus3it/watchmaker.svg)](./LICENSE)
[![Build and Test Status](https://github.com/plus3it/watchmaker/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/plus3it/watchmaker/actions/workflows/build.yml)
[![Release and Publish Status](https://github.com/plus3it/watchmaker/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/plus3it/watchmaker/actions/workflows/release.yml)
[![Latest Version](https://img.shields.io/pypi/v/watchmaker.svg?label=version)](https://pypi.python.org/pypi/watchmaker)

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
