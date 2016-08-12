#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import os

from setuptools import find_packages, setup

setup(
    name='watchmaker',
    version='0.1',
    author='Plus3IT Maintainers of Watchmaker',
    author_email='projects@plus3it.com',
    url='https://github.com/plus3it/watchmaker',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    scripts=[os.path.join('scripts', 'Watchmaker.py')],
    install_requires=[
        "botocore",
        "boto3",
        "validators",
        "PyYAML"
    ]
)
