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
import sys
import urllib.request
import unittest
from unittest.mock import patch, MagicMock

from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider


# def test_reading_invalid_vendor_file():
#     provider = AWSProvider()
#     assert provider.check_vendor_file() is False

@patch('urllib.request.urlopen')
def test_valid_metadata_server_check(mock_urlopen):
    cm = MagicMock()
    cm.getcode.return_value = 200
    cm.read.return_value = '{"imageId": "ami-12312412", "instanceId": "i-ec12as"}'.encode('utf8')
    cm.__enter__.return_value = cm
    mock_urlopen.return_value = cm

    provider = AWSProvider()
    provider.metadata_url = "http://testing_metadata_url.com"
    assert provider.check_metadata_server() is True



# def test_invalid_metadata_server_check():
#     mocking_url = "http://testing_metadata_url.com"
#     responses.add(
#         responses.GET,
#         "http://testing_metadata_url.com",
#         json={"imageId": "some_ID", "instanceId": "some_Instance"},
#     )

#     provider = AWSProvider()
#     provider.metadata_url = mocking_url
#     assert provider.check_metadata_server() is False
