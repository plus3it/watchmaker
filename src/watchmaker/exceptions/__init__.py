# -*- coding: utf-8 -*-
"""Watchmaker exceptions module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)


class WatchmakerException(Exception):
    """An unknown error occurred."""


class InvalidValue(WatchmakerException):
    """Passed an invalid value."""
