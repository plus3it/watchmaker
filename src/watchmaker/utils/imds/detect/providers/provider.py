# -*- coding: utf-8 -*-
"""Abstract Provider."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

try:
    from abc import ABC, abstractmethod
except (ImportError, NameError):
    from abc import ABCMeta, abstractmethod


class AbstractProvider(ABC):
    """
    Abstract class representing a cloud provider.
    All concrete cloud providers should implement this.
    """

    identifier = "unknown"
    url_timeout = 5

    @abstractmethod
    def identify(self):
        pass  # pragma: no cover

    @abstractmethod
    def check_metadata_server(self):
        pass  # pragma: no cover

    @abstractmethod
    def check_vendor_file(self):
        pass  # pragma: no cover
