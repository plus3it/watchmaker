# -*- coding: utf-8 -*-
"""Loads helper utility modules and functions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import ssl

import backoff

from watchmaker.utils import urllib


def scheme_from_uri(uri):
    """Return a scheme from a parsed uri."""
    # Handle case where path does not contain a scheme
    # i.e. '/abspath/foo' or 'relpath/foo'
    # Do not test `if parts.scheme` because of how urlparse handles Windows
    # file paths -- i.e. 'C:\\foo' => scheme = 'c' :(
    return uri.scheme if '://' in urllib.parse.urlunparse(uri) else 'file'


def uri_from_filepath(filepath):
    """Return a URI compatible with urllib, handling URIs and file paths."""
    parts = urllib.parse.urlparse(filepath)
    scheme = scheme_from_uri(parts)

    if scheme != 'file':
        # Return non-file paths unchanged
        return filepath

    # Expand relative file paths and convert them to uri-style
    path = urllib.request.pathname2url(os.path.abspath(os.path.expanduser(
        ''.join([x for x in [parts.netloc, parts.path] if x]))))

    return urllib.parse.urlunparse((scheme, '', path, '', '', ''))


def basename_from_uri(uri):
    """Return the basename/filename/leaf part of a URI."""
    # Do not split on '/' and return the last part because that will also
    # include any query in the uri. Instead, parse the uri.
    return os.path.basename(urllib.parse.urlparse(uri).path)


@backoff.on_exception(backoff.expo, urllib.error.URLError, max_tries=5)
def urlopen_retry(uri):
    """Retry urlopen on exception."""
    kwargs = {}
    try:
        # trust the system's default CA certificates
        # proper way for 2.7.9+ on Linux
        if uri.startswith("https://"):
            kwargs['context'] = ssl.create_default_context(
                ssl.Purpose.CLIENT_AUTH
            )
    except AttributeError:
        pass

    return urllib.request.urlopen(uri, **kwargs)
