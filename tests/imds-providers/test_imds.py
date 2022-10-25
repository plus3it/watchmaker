# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.utils.imds.detect import is_excluded, provider
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider


@patch.object(AWSProvider,
              'identify',
              return_value=True)
@patch.object(AzureProvider,
              'identify',
              return_value=False)
def test_provider_aws(aws_provider_mock, aure_provider_mock):
    """Test provider is AWS."""
    assert provider() == "aws"


@patch.object(AWSProvider,
              'identify',
              return_value=False)
@patch.object(AzureProvider,
              'identify',
              return_value=True)
@patch.object(AzureProvider, 'check_vendor_file', return_value=False)
def test_provider_azure(aws_provider_mock,
                        aure_provider_mock,
                        azure_check_vendor_file_mock):
    """Test provider is Azure."""
    assert provider() == "azure"


@patch.object(AWSProvider,
              'identify',
              return_value=False)
@patch.object(AzureProvider,
              'identify',
              return_value=False)
def test_provider_not_aws_or_azure(aws_provider_mock, aure_provider_mock):
    """Test provider is unknown."""
    assert provider() == "unknown"


def test_provider_excluded():
    """Test provider is excluded."""
    excluded = ["aws"]
    assert is_excluded("aws", excluded) is True


def test_provider_not_excluded():
    """Test provider is not excluded."""
    excluded = ["gcp"]
    assert is_excluded("aws", excluded) is False


def test_provider_no_exclusions():
    """Test provider is not excluded when no exclusions provided"""
    assert is_excluded("aws") is False
