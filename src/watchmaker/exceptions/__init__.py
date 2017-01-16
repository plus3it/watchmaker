"""Watchmaker exception module."""


class WatchmakerException(Exception):
    """An unknown error occurred."""


class InvalidValue(WatchmakerException):
    """Passed an invalid value."""
