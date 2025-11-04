"""Watchmaker exceptions module."""


class WatchmakerError(Exception):
    """An unknown error occurred."""


class InvalidComputerNameError(WatchmakerError):
    """Exception raised when computer_name does not match pattern provided."""

    def __init__(self, computer_name, pattern):
        """Initialize with computer name and pattern."""
        super().__init__(
            f"Computer name: {computer_name} does not match pattern {pattern}",
        )


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


class StatusConfigError(WatchmakerError):
    """Exception raised when status configuration is invalid."""


class InvalidRegexPatternError(WatchmakerError):
    """Exception raised when regex pattern is invalid."""


class MultiplePathsMatchError(WatchmakerError):
    """Exception raised when multiple paths match a glob pattern."""


class PathNotFoundError(WatchmakerError):
    """Exception raised when expected path is not found."""


class CloudProviderDetectionError(WatchmakerError):
    """Exception raised when cloud environment detection fails."""

    def __init__(self, provider_identifier):
        """Initialize with provider identifier."""
        super().__init__(
            f"Required Provider detected that is missing prereqs: "
            f"{provider_identifier}",
        )


class MissingURLParamError(WatchmakerError):
    """Exception raised when required URL parameter is missing."""


# Deprecated/renamed exceptions
WatchmakerException = WatchmakerError
InvalidValue = InvalidValueError
OuPathRequired = OuPathRequiredError
