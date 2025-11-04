"""Abstract Provider."""

import abc


class AbstractProvider(abc.ABC):
    """
    Abstract class representing a cloud provider.

    All concrete cloud providers should implement this.
    """

    DEFAULT_TIMEOUT = 5
    identifier = "unknown"

    @abc.abstractmethod
    def identify(self):
        """Identify provider type."""
        # pragma: no cover

    @abc.abstractmethod
    def check_metadata_server(self):
        """Identify via metadata server."""
        # pragma: no cover
