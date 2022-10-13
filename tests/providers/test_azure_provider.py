# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import pytest

try:
    from unittest.mock import MagicMock, call, patch
except ImportError:
    from mock import MagicMock, call, patch

from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider


def test_reading_invalid_vendor_file():
    provider = AzureProvider()
    assert provider.check_vendor_file() is False


@patch.object(AzureProvider, '_AzureProvider__is_valid_server')
def test_metadata_server_check(provider_mock):
    provider = AzureProvider()

    provider_mock.return_value = True

    assert provider.check_metadata_server() is True

    provider_mock.return_value = False

    assert provider.check_metadata_server() is False
