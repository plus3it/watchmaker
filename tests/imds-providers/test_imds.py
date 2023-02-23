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

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.utils.imds.detect import provider
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider


@patch.object(AWSProvider, "identify", return_value=True)
@patch.object(AzureProvider, "identify", return_value=False)
def test_provider_aws(aws_provider_mock, azure_provider_mock):
    """Test provider is AWS."""
    assert provider(["aws", "azure"]) == "aws"


@patch.object(AWSProvider, "identify", return_value=False)
@patch.object(AzureProvider, "identify", return_value=True)
@patch.object(AzureProvider, "check_vendor_file", return_value=False)
def test_provider_azure(
    aws_provider_mock, azure_provider_mock, azure_check_vendor_file_mock
):
    """Test provider is Azure."""
    assert provider(["aws", "azure"]) == "azure"


@patch.object(AWSProvider, "identify", return_value=False)
@patch.object(AzureProvider, "identify", return_value=False)
def test_provider_not_aws_or_azure(aws_provider_mock, azure_provider_mock):
    """Test provider is unknown."""
    assert provider(["aws", "azure"]) == "unknown"


@patch.object(AWSProvider, "identify", return_value=False)
@patch.object(AzureProvider, "identify", return_value=False)
def test_none_provider(aws_provider_mock, azure_provider_mock):
    """Test provider is unknown."""
    assert provider(None) == "unknown"


@pytest.mark.skipif(True, reason="Test should be manually run.")
def test_provider_detect():
    """Test provider is unknown."""
    assert provider(["aws", "azure"]) == "unknown"
