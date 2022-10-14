# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider


def test_reading_invalid_vendor_file():
    provider = AWSProvider()
    assert provider.check_vendor_file() is False


@patch.object(AWSProvider, '_AWSProvider__get_data_from_server')
def test_metadata_server_check(provider_mock):
    provider = AWSProvider()

    provider_mock.return_value = (
        '{"imageId": "ami-12312412", "instanceId": "i-ec12as"}'.encode("utf8")
    )

    assert provider.check_metadata_server() is True

    provider_mock.return_value = (
        '{"imageId": "some_ID", "instanceId": "some_Instance"}'.encode("utf8")
    )

    assert provider.check_metadata_server() is False
