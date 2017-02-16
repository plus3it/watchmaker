#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Append a build number to a version string. See Pep 440."""

from __future__ import absolute_import
from __future__ import print_function

import io
import os
import re


PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir)
)
VERSION_FILE_PATHS = ('src', 'watchmaker', '__init__.py')
VERSION_FILE = os.path.join(PROJECT_ROOT, *VERSION_FILE_PATHS)
BUILD_NUMBER = os.environ.get('TRAVIS_BUILD_NUMBER', '')


def replace(file_path, pattern, repl, flags=0):
    """Replace a pattern in a file."""
    with io.open(file_path, mode="r+", newline='') as fh_:
        file_contents = fh_.read()
        file_contents = re.sub(pattern, repl, file_contents, flags=flags)
        fh_.seek(0)
        fh_.truncate()
        fh_.write(file_contents)


def append_build(build, version_file):
    """Append a build number to a version string in a file."""
    # The version line must have the form
    # __version__ = 'ver'
    pattern = r"^(__version__ = ['\"])([^'\"]*)(['\"])"
    repl = r"\g<1>\g<2>{0}\g<3>".format(build)
    print(
        'Updating version in version_file "{0}" with build "{1}"'
        .format(version_file, build)
    )
    replace(version_file, pattern, repl, flags=re.M)


def main(args):
    """Process args and set version."""
    skip = args.skip
    build = args.build
    version_file = args.version_file

    if skip:
        print(
            'Not updating version for this build, `skip` set to "{0}"'
            .format(skip)
        )
    else:
        append_build(build, version_file)


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--skip',
        default=False,
        help=(
            'If set to any non-false value, skips updating the version. '
            '(default: {0})'.format(False)
        )
    )
    parser.add_argument(
        '--build',
        default=BUILD_NUMBER,
        help=(
            'Build number to append to the version. Will default to the env '
            'TRAVIS_BUILD_NUMBER or an empty string. (default: {0})'
            .format(BUILD_NUMBER)
        )
    )
    parser.add_argument(
        '--version-file',
        default=VERSION_FILE,
        help=(
            'Path to the file containing the version string. '
            '(default: {0})'.format(VERSION_FILE)
        )
    )

    args = parser.parse_args()
    main(args)
