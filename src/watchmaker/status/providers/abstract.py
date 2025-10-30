"""Abstract Status Provider."""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class AbstractStatusProvider:
    """
    Abstract class representing a watchmaker status cloud provider.

    All concrete watchmaker status cloud providers should implement this.
    """

    DEFAULT_TIMEOUT = 5
    identifier = "unknown"

    @abc.abstractmethod
    def initialize(self):
        """Initialize provider."""
        # pragma: no cover

    @abc.abstractmethod
    def update_status(self, key, status, required):
        """Identify via metadata server."""
        # pragma: no cover
