# -*- coding: utf-8 -*-
"""Loads helper utility modules and functions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os

from watchmaker.utils.urllib import parse, request


def path_to_uri(filepath):
    """Convert a file path to a URI compatible with urllib."""
    parts = parse.urlparse(filepath)

    # Handle case where path does not contain a scheme
    # i.e. '/abspath/foo' or 'relpath/foo'
    # Do not test `if parts.scheme` because of how urlparse handles Windows
    # file paths -- i.e. 'C:\\foo' => scheme = 'c' :(
    scheme = parts.scheme if '://' in filepath else 'file'

    if scheme != 'file':
        # Return non-file paths unchanged
        return filepath

    # Expand relative file paths and convert them to url-style
    path = request.pathname2url(os.path.abspath(os.path.expanduser(
        ''.join([x for x in [parts.netloc, parts.path] if x]))))

    return parse.urlunparse((scheme, '', path, '', '', ''))
