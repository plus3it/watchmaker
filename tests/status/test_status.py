# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import yaml

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
def test_status(
    aws_provider_mock,
    azure_provider_mock,
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
