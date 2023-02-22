# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import os

from watchmaker.config import get_configs

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch("watchmaker.utils.imds.detect.provider", return_value="aws")
def test_config_with_suppported_status_provider(mock_provider):
    """Test config that has the status block and supported provider."""
    worker_args = {
        'admin_groups': 'None',
        'admin_users': 'None',
        'computer_name': 'None',
        'salt_states': 'None',
        'ou_path': 'None'
    }
    config, status_config = \
        get_configs(
            "linux",
            worker_args,
            os.path.join("tests", "resources", "config_with_status.yaml"))
    assert config is not None
    assert status_config is not None


@patch("watchmaker.utils.imds.detect.provider", return_value="unknown")
def test_config_without_status_config(mock_provider):
    """Test config that does not have status block or provider."""
    worker_args = {
        'admin_groups': 'None',
        'admin_users': 'None',
        'computer_name': 'None',
        'salt_states': 'None',
        'ou_path': 'None'
    }
    config, status_config = \
        get_configs(
            "linux",
            worker_args,
            os.path.join("tests", "resources", "config_without_status.yaml"))
    assert config is not None
    assert status_config is None
