#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import os
import re

from setuptools import find_packages, setup


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


def find_version(*file_paths):
    # Read the version number from a source file.
    # Why read it, and not import?
    # see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
    version_file = read(*file_paths, encoding='latin1')

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='watchmaker',
    version=find_version('src', 'watchmaker', '__init__.py'),
    author='Plus3IT Maintainers of Watchmaker',
    author_email='projects@plus3it.com',
    url='https://github.com/plus3it/watchmaker',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'watchmaker = watchmaker.cli:main',
            'wam = watchmaker.cli:main',
        ]
    },
    install_requires=[
        "six",
        "PyYAML"
    ]
)
