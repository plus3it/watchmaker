# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider

# @patch.object(AWSProvider, '_AWSProvider__get_data_from_server')
#     provider_mock.return_value = (
#         '{"imageId": "ami-12312412", "instanceId": "i-ec12as"}' \
#          .encode("utf8")
#     )


# def test_metadata_data_server_call_fail():
#     """Test calling the real metadata server and failing."""
#     provider = AWSProvider()
#     assert provider.check_metadata_server() is False


@patch.object(
    AWSProvider,
    "_AWSProvider__get_data_from_server",
    return_value=(
        '{"imageId": "ami-12312412", \
                            "instanceId": "i-ec12as"}'.encode(
            "utf8"
        )
    ),
)
def test_aws_valid_metadata_data_from_server(provider_mock):
    """Test valid server data response for aws provider identification."""
    provider = AWSProvider()
    assert provider.check_metadata_server() is True


@patch.object(
    AWSProvider,
    "_AWSProvider__get_data_from_server",
    return_value=(
        '{"imageId": "some_ID", \
                              "instanceId": "some_Instance"}'.encode(
            "utf8"
        )
    ),
)
def test_aws_invalid_metadata_data_from_server(provider_mock):
    """Test invalid server data response for aws provider identification."""
    provider = AWSProvider()
    assert provider.check_metadata_server() is False


@patch.object(
    AWSProvider, "_AWSProvider__get_data_from_server", return_value=(None)
)
def test_aws_no_metadata_data_from_server(provider_mock):
    """Test no server data response for aws provider identification."""
    provider = AWSProvider()
    assert provider.check_metadata_server() is False


@patch.object(AWSProvider, "_AWSProvider__is_valid_server", return_value=True)
def test_aws_metadata_valid_server(provider_mock):
    """Test valid server for aws provider identification."""
    provider = AWSProvider()
    assert provider.check_metadata_server() is True


@patch.object(AWSProvider, "_AWSProvider__is_valid_server", return_value=False)
def test_aws_metadata_invalid_server(provider_mock):
    """Test invalid server for aws provider identification."""
    provider = AWSProvider()
    assert provider.check_metadata_server() is False


@patch.object(
    AWSProvider,
    "_AWSProvider__get_file_contents",
    return_value=b"provider is amazon aws",
)
def test_aws_valid_vendor_file(provider_mock):
    """Tests valid vendor file."""
    provider = AWSProvider()
    assert provider.check_vendor_file() is True


@patch.object(
    AWSProvider,
    "_AWSProvider__get_file_contents",
    return_value=b"provider unknown",
)
def test_aws_invalid_vendor_file(provider_mock):
    """Tests invalid vendor file."""
    provider = AWSProvider()
    assert provider.check_vendor_file() is False


@patch.object(
    AWSProvider, "_AWSProvider__get_file_contents", return_value=None
)
def test_aws_no_response_vendor_file(provider_mock):
    """Tests no response while reading vendor file."""
    provider = AWSProvider()
    assert provider.check_vendor_file() is False
