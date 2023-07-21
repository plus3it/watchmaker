# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import json

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider


@patch.object(
    AWSProvider,
    "_AWSProvider__call_urlopen_retry",
    return_value=(
        json.dumps({"imageId": "ami-12312412", "instanceId": "i-ec12as"})
    ),
)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_identify_is_valid(mock_urlopen, mock_request_token):
    """Test valid server data response for aws provider identification."""
    provider = AWSProvider()
    assert provider.identify() is True


@patch.object(
    AWSProvider,
    "_AWSProvider__call_urlopen_retry",
    return_value=(
        json.dumps({"imageId": "ami-12312412", "instanceId": "i-ec12as"})
    ),
)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_metadata_server_is_valid(mock_urlopen, mock_request_token):
    """Test valid server data response for aws provider identification."""
    provider = AWSProvider()
    assert provider.check_metadata_server() is True


@patch.object(
    AWSProvider,
    "_AWSProvider__call_urlopen_retry",
    return_value=(
        json.dumps({"imageId": "not-valid", "instanceId": "etc-ec12as"})
    ),
)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_metadata_server_is_invalid(mock_urlopen, mock_request_token):
    """Test invalid server data response for aws provider identification."""
    provider = AWSProvider()
    assert provider.check_metadata_server() is False


@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=("abcdefgh1234546"),
)
@patch.object(
    AWSProvider,
    "_AWSProvider__call_urlopen_retry",
    return_value=(None),
)
def test_aws_metadata_headers(mock_request_token, mock_urlopen):
    """Test token is not saved to imds_token."""
    provider = AWSProvider()
    assert provider.get_metadata_request_headers() == {
        "X-aws-ec2-metadata-token": "abcdefgh1234546"
    }


@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
@patch.object(
    AWSProvider,
    "_AWSProvider__call_urlopen_retry",
    return_value=(None),
)
def test_aws_metadata_headers_none(mock_request_token, mock_urlopen):
    """Test token is not saved to imds_token."""
    provider = AWSProvider()
    assert provider.get_metadata_request_headers() is None
