# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import yaml

from watchmaker.exceptions import StatusProviderError

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.status import Status
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider


@patch.object(AWSProvider, "identify", return_value=True)
@patch.object(AzureProvider, "identify", return_value=False)
@patch(
    "watchmaker.config.status.get_cloud_ids_with_prereqs",
    return_value=["aws", "azure"],
)
def test_status(
    aws_provider_mock, azure_provider_mock, supported_identifiers_mock
):
    """Test provider is AWS."""
    data = """
    status:
      providers:
        - key: "WatchmakerStatus"
          required: False
          provider_type: "aws"
        - key: "WatchmakerStatus"
          required: False
          provider_type: "azure"
    """
    config = yaml.load(data, Loader=yaml.Loader)
    config_status = config.get("status", None)
    status = Status(config_status)
    detected_providers = status.get_detected_providers()
    assert len(detected_providers) == 1
    assert detected_providers[0] == AWSProvider.identifier


@patch.object(AWSProvider, "identify", return_value=False)
@patch.object(AzureProvider, "identify", return_value=True)
@patch(
    "watchmaker.config.status.get_cloud_ids_with_prereqs",
    return_value=[],
)
@patch(
    "watchmaker.config.status.get_cloud_ids_missing_prereqs",
    return_value=["aws", "azure"],
)
def test_req_status_provider(
    aws_provider_mock,
    azure_provider_mock,
    supported_identifiers_mock,
    missing_prereqs_mock,
):
    """Test provider is AWS."""
    data = """
    status:
      providers:
        - key: "WatchmakerStatus"
          required: False
          provider_type: "aws"
        - key: "WatchmakerStatus"
          required: True
          provider_type: "azure"
    """
    config = yaml.load(data, Loader=yaml.Loader)
    config_status = config.get("status", None)

    try:
        Status(config_status)
    except StatusProviderError as e:
        assert (
            str(e)
            == "Required Provider detected that is missing prereqs: azure"
        )
