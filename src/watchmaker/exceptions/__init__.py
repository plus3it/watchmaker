"""Watchmaker exceptions module."""


class WatchmakerError(Exception):
    """An unknown error occurred."""


class InvalidComputerNameError(WatchmakerError):
    """Exception raised when computer_name does not match pattern provided."""


class InvalidValueError(WatchmakerError):
    """Passed an invalid value."""


class StatusProviderError(WatchmakerError):
    """Status Error."""


class CloudDetectError(WatchmakerError):
    """Cloud Detect Error."""


class InvalidProviderError(WatchmakerError):
    """Invalid Provider Error."""


class OuPathRequiredError(Exception):
    """Exception raised when the OU path is required but not provided."""


# Deprecated/renamed exceptions
WatchmakerException = WatchmakerError
InvalidValue = InvalidValueError
OuPathRequired = OuPathRequiredError
