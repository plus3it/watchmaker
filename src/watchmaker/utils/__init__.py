"""Loads helper utility modules and functions."""

import os
import platform
import shutil
import ssl
import warnings
from pathlib import Path

import backoff

from watchmaker.utils import urllib_utils


def scheme_from_uri(uri):
    """Return a scheme from a parsed uri."""
    # Handle case where path does not contain a scheme
    # i.e. '/abspath/foo' or 'relpath/foo'
    # Do not test `if parts.scheme` because of how urlparse handles Windows
    # file paths -- i.e. 'C:\\foo' => scheme = 'c' :(
    return uri.scheme if "://" in urllib_utils.parse.urlunparse(uri) else "file"


def uri_from_filepath(filepath):
    """Return a URI compatible with urllib, handling URIs and file paths."""
    # Convert Path to str for urlparse compatibility
    filepath = str(filepath) if isinstance(filepath, Path) else filepath

    parts = urllib_utils.parse.urlparse(filepath)
    scheme = scheme_from_uri(parts)

    if scheme != "file":
        # Return non-file paths unchanged
        return filepath

    # Expand relative file paths and convert them to uri-style
    combined_path = "".join([x for x in [parts.netloc, parts.path] if x])
    path = urllib_utils.request.pathname2url(
        str(Path(combined_path).expanduser().resolve()),
    )

    return urllib_utils.parse.urlunparse((scheme, "", path, "", "", ""))


def basename_from_uri(uri):
    """Return the basename/filename/leaf part of a URI."""
    # Do not split on '/' and return the last part because that will also
    # include any query in the uri. Instead, parse the uri.
    return Path(urllib_utils.parse.urlparse(uri).path).name


@backoff.on_exception(backoff.expo, urllib_utils.error.URLError, max_tries=5)
def urlopen_retry(uri, timeout=None):
    """Retry urlopen on exception."""
    kwargs = {}
    if timeout:
        kwargs["timeout"] = timeout
    try:
        # trust the system's default CA certificates
        # proper way for 2.7.9+ on Linux
        url = uri if isinstance(uri, str) else uri.full_url

        if url.startswith("https://"):
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

            # Workaround for old OpenSSL bug on Red Hat 8 systems
            # See: https://github.com/astral-sh/python-build-standalone/issues/858
            ssl_cert = Path("/etc/ssl/cert.pem")
            el8_cert = Path("/etc/pki/tls/cert.pem")
            if not ssl_cert.exists() and el8_cert.exists():
                context.load_verify_locations(cafile=str(el8_cert))

            kwargs["context"] = context
    except AttributeError:
        pass

    return urllib_utils.request.urlopen(uri, **kwargs)


def _add_long_path_prefix(path):
    """Add Windows long path prefix if needed."""
    path_str = str(path)
    if not path_str.startswith(r"\\?"):
        return Path(rf"\\?\{path_str}")
    return path


def copytree(src, dst, *, force=False, **kwargs):
    r"""
    Copy OS directory trees from source to destination.

    On Windows, automatically handles paths exceeding the MAX_PATH limit (260 chars)
    by converting to extended-length paths with the \\?\ prefix when necessary.

    Args:
        src: (:obj:`Path`)
            Source directory tree to be copied.
            (*Default*: None)

        dst: (:obj:`Path`)
            Destination where directory tree is to be copied.
            (*Default*: None)

        force: (:obj:`bool`)
            Whether to delete destination prior to copy.
            (*Default*: ``False``)

        **kwargs:
            Additional keyword arguments to pass to :func:`shutil.copytree`.

    """
    # On Windows, handle paths that may exceed MAX_PATH (260 characters)
    # References:
    # - https://discuss.python.org/t/request-for-pathlib-path-as-unc/91271/5
    # - https://github.com/python/cpython/issues/71917
    if platform.system() == "Windows" and "copy_function" not in kwargs:
        # Threshold for applying long path prefix (allows ~60 char headroom)
        long_path_threshold = 200

        def long_path_copy(src_file, dst_file, **copy_kwargs):
            """Copy with long path support when paths exceed threshold."""
            src_path = Path(src_file)
            dst_path = Path(dst_file)

            # Apply \\?\ prefix if paths approach MAX_PATH (260 chars)
            # Check each path independently and only prefix if needed
            if len(str(src_path)) > long_path_threshold:
                src_path = _add_long_path_prefix(src_path)

            if len(str(dst_path)) > long_path_threshold:
                dst_path = _add_long_path_prefix(dst_path)

            shutil.copy2(src_path, dst_path, **copy_kwargs)

        kwargs["copy_function"] = long_path_copy

    if force and dst.exists():
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
            "`null` instead."
        )
        log.warning(deprecate_msg)
        warnings.warn(deprecate_msg, DeprecationWarning, stacklevel=2)

    return value


def clean_none(value):
    """Convert string 'None' to None."""
    if str(value).lower() == "none":
        return None

    return value


def copy_subdirectories(src_dir, dest_dir, log=None):
    """Copy subdirectories within given src dir into dest dir."""
    for subdir in next(os.walk(src_dir))[1]:
        dest_subdir = dest_dir / subdir
        if not subdir.startswith(".") and not dest_subdir.exists():
            src_subdir = src_dir / subdir
            copytree(src_subdir, dest_subdir)
            if log:
                log.info(
                    "Copied from %s to %s",
                    src_subdir,
                    dest_subdir,
                )
