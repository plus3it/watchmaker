# -*- coding: utf-8 -*-
"""Watchmaker exceptions module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)


class WatchmakerError(Exception):
    """An unknown error occurred."""


class InvalidValueError(WatchmakerError):
    """Passed an invalid value."""


class StatusProviderError(WatchmakerError):
    """Status Error."""


class CloudDetectError(WatchmakerError):
    """Cloud Detect Error."""


class InvalidProviderError(WatchmakerError):
    """Invalid Provider Error."""


# Deprecated/renamed exceptions
WatchmakerException = WatchmakerError
InvalidValue = InvalidValueError
