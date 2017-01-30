# -*- coding: utf-8 -*-
"""Watchmaker exceptions module."""


class WatchmakerException(Exception):
    """An unknown error occurred."""


class InvalidValue(WatchmakerException):
    """Passed an invalid value."""
