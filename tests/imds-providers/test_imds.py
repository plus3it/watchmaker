"""Providers main test module."""

import pytest

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from unittest.mock import patch

from watchmaker.utils.imds.detect import provider
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider


@patch.object(AWSProvider, "identify", return_value=True)
@patch.object(AzureProvider, "identify", return_value=False)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_provider_aws(aws_provider_mock, azure_provider_mock, aws_token_mock):
    """Test provider is AWS."""
    assert provider(["aws", "azure"]).identifier == "aws"


@patch.object(AWSProvider, "identify", return_value=False)
@patch.object(AzureProvider, "identify", return_value=True)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_provider_azure(aws_provider_mock, azure_provider_mock, aws_token_mock):
    """Test provider is Azure."""
    assert provider(["aws", "azure"]).identifier == "azure"


@patch.object(AWSProvider, "identify", return_value=False)
@patch.object(AzureProvider, "identify", return_value=False)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_provider_not_aws_or_azure(
    aws_provider_mock,
    azure_provider_mock,
    aws_token_mock,
):
    """Test provider is unknown."""
    assert provider(["aws", "azure"]).identifier == "unknown"


@patch.object(AWSProvider, "identify", return_value=False)
@patch.object(AzureProvider, "identify", return_value=False)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_none_provider(aws_provider_mock, azure_provider_mock, aws_token_mock):
    """Test provider is unknown."""
    assert provider(None).identifier == "unknown"


@pytest.mark.skipif(True, reason="Test should be manually run.")
def test_provider_detect():
    """Test provider is unknown."""
    assert provider(["aws", "azure"]).identifier == "unknown"
