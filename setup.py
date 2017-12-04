#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Watchmaker setup script."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import io
import os

from setuptools import setup


def read(*names, **kwargs):
    """Read a file."""
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


def parse_md_to_rst(files):
    """Read Markdown files and convert them to ReStructured Text."""
    rst = []
    try:
        from m2r import parse_from_file
        for name in files:
            rst += [parse_from_file(name)]
    except ImportError:
        # m2r may not be installed in user environment
        for name in files:
            rst += [read(name)]
    return '\n'.join(rst)


setup(
    long_description=parse_md_to_rst(['README.md', 'CHANGELOG.md']),
    package_dir={'': str('src')}
)
