# -*- coding: utf-8 -*-
"""Abstract Status Provider."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import abc

import six


class StatusProviderError(Exception):
    """Status Exception."""


@six.add_metaclass(abc.ABCMeta)
class AbstractStatusProvider():
    """Abstract class representing a watchmaker status cloud provider.

    All concrete watchmaker status cloud providers should implement this.
    """

    identifier = "unknown"

    @abc.abstractmethod
    def initialize(self):
        """Initialize provider."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def tag_resource(self, key, status, required):
        """Identify via metadata server."""
        pass  # pragma: no cover