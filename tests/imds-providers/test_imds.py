# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import pytest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.utils.imds.detect import provider
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider


@patch.object(AWSProvider,
              'identify',
              return_value='aws')
@patch.object(AzureProvider,
              'identify',
              return_value='unknown')
def test_provider_aws(aws_provider_mock, azure_provider_mock):
    """Test provider is AWS."""
    assert provider() == "aws"


@patch.object(AWSProvider,
              'identify',
              return_value='unknown')
@patch.object(AzureProvider,
              'identify',
              return_value='azure')
@patch.object(AzureProvider, 'check_vendor_file', return_value=False)
def test_provider_azure(aws_provider_mock,
                        azure_provider_mock,
                        azure_check_vendor_file_mock):
    """Test provider is Azure."""
    assert provider() == "azure"


@patch.object(AWSProvider,
              'identify',
              return_value='unknown')
@patch.object(AzureProvider,
              'identify',
              return_value='unknown')
def test_provider_not_aws_or_azure(aws_provider_mock, azure_provider_mock):
    """Test provider is unknown."""
    assert provider() == "unknown"


@pytest.mark.skipif(True,
                    reason="Test should be manually run.")
def test_provider_detect():
    """Test provider is unknown."""
    assert provider() == "unknown"
