# -*- coding: utf-8 -*-
"""Loads helper utility modules and functions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import shutil
import ssl
import warnings

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
                ssl.Purpose.SERVER_AUTH
            )
    except AttributeError:
        pass

    # pylint: disable=consider-using-with
    return urllib.request.urlopen(uri, **kwargs)


def copytree(src, dst, force=False, **kwargs):
    r"""
    Copy OS directory trees from source to destination.

    Args:
        src: (:obj:`str`)
            Source directory tree to be copied.
            (*Default*: None)

        dst: (:obj:`str`)
            Destination where directory tree is to be copied.
            (*Default*: None)

        force: (:obj:`bool`)
            Whether to delete destination prior to copy.
            (*Default*: ``False``)

    """
    if force and os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst, **kwargs)


def config_none_deprecate(check_value, log):
    r"""
    Warn if variable is the string 'None' rather than Pythonic `None`.

    If it is the string 'None', this warns and returns Pythonic `None`.
    Otherwise, the variable is returned unchanged.

    Args:
        check_value: (:obj:`str`)
            Variable to be checked for string 'None' (case-insenstive).

        log: (:obj:`logging.Logger`)
            Logger where deprecation warning will be made.

    """
    value = clean_none(check_value)

    if check_value and value is None:
        deprecate_msg = (
            'Use of "None" (string) as a config value is deprecated. Use '
            '`null` instead.')
        log.warn(deprecate_msg)
        warnings.warn(deprecate_msg, DeprecationWarning)

    return value


def clean_none(value):
    """Convert string 'None' to None."""
    if str(value).lower() == 'none':
        return None

    return value


def copy_subdirectories(src_dir, dest_dir, log=None):
    """Copy subdirectories within given src dir into dest dir."""
    for subdir in next(os.walk(src_dir))[1]:
        if (
            not subdir.startswith('.') and
            not os.path.exists(os.sep.join((dest_dir, subdir)))
        ):
            copytree(
                os.sep.join((src_dir, subdir)),
                os.sep.join((dest_dir, subdir))
            )
            if log:
                log.info('Copied from %s to %s',
                         os.sep.join((src_dir, subdir)),
                         os.sep.join((dest_dir, subdir)))
