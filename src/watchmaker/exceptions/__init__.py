# -*- coding: utf-8 -*-
"""Watchmaker exceptions module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)


class WatchmakerError(Exception):
    """An unknown error occurred."""


class InvalidValueError(WatchmakerError):
    """Passed an invalid value."""


# Deprecated/renamed exceptions
WatchmakerException = WatchmakerError
InvalidValue = InvalidValueError
