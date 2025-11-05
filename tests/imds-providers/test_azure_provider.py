"""Providers main test module."""

from unittest.mock import patch

from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider


@patch.object(AzureProvider, "_AzureProvider__is_valid_server")
def test_metadata_server_check(provider_mock):
    """Tests metadata server check."""
    provider = AzureProvider()

    provider_mock.return_value = True

    assert provider.check_metadata_server() is True

    provider_mock.return_value = False

    assert provider.check_metadata_server() is False
