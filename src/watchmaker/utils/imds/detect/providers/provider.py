# -*- coding: utf-8 -*-
"""Abstract Provider."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class AbstractProvider():
    """Abstract class representing a cloud provider.

    All concrete cloud providers should implement this.
    """

    DEFAULT_TIMEOUT = 5
    identifier = 'unknown'

    @abc.abstractmethod
    def identify(self):
        """Identify provider type."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def check_metadata_server(self):
        """Identify via metadata server."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def check_vendor_file(self):
        """Identify via vendor file."""
        pass  # pragma: no cover
