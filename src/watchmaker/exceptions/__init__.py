"""Watchmaker exception module."""

import logging


class ExcLevel:
    """Define exception levels."""

    Error = 1
    Critical = 2


class WatchmakerException(Exception):
    """An unknown error occurred."""


class InvalidValue(WatchmakerException):
    """Passed an invalid value."""


def wm_exit(message, level, has_exc):
    if level == ExcLevel.Error:
        logging.error(message, exc_info=has_exc)

    if level == ExcLevel.Critical:
        logging.critical(message, exc_info=has_exc)

    raise
