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

from watchmaker.utils.imds.detect import provider
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider

@patch.object(AWSProvider,
              '_AWSProvider__get_data_from_server',
            return_value = ('{"imageId": "ami-12312412", "instanceId": "i-ec12as"}'.encode("utf8")))
def test_aws_provider(provider_mock):
    assert provider() == "aws"

@patch.object(AWSProvider,
              '_AWSProvider__get_data_from_server',
              return_value = ('{"imageId": "some_ID", "instanceId": "some_Instance"}'.encode("utf8")))
def test_not_aws_provider(provider_mock):
    assert provider() == "unknown"

@patch.object(AzureProvider, '_AzureProvider__is_valid_server', return_value=True)
@patch.object(AzureProvider, 'check_vendor_file', return_value=False)
def test_azure_provider(mock_is_valid_server, mock_check_vendor_file):
    assert provider() == "azure"

@patch.object(AzureProvider, '_AzureProvider__is_valid_server', return_value=False)
@patch.object(AzureProvider, 'check_vendor_file', return_value=False)
def test_not_azure_provider(mock_is_valid_server, mock_check_vendor_file):
    assert provider() == "unknown"

