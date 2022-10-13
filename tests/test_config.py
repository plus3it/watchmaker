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

import pytest
from watchmaker.utils.config.watchmaker_config import get_watchmaker_configs

try:
    from unittest.mock import MagicMock, call, patch
except ImportError:
    from mock import MagicMock, call, patch

@patch("watchmaker.utils.imds.detect.provider", return_value="aws")
def test_config_with_status(mock_provider):
    worker_args = {
        'admin_groups': 'None',
        'admin_users': 'None',
        'computer_name': 'None',
        'salt_states': 'None',
        'ou_path': 'None'
    }
    config, status_config = get_watchmaker_configs("linux", worker_args, os.path.join("tests", "resources", "config_with_status.yaml"))
    assert config is not None
    assert status_config is not None

@patch("watchmaker.utils.imds.detect.provider", return_value="gcp")
def test_config_without_status_provider(mock_provider):
    worker_args = {
        'admin_groups': 'None',
        'admin_users': 'None',
        'computer_name': 'None',
        'salt_states': 'None',
        'ou_path': 'None'
    }
    config, status_config = get_watchmaker_configs("linux", worker_args, os.path.join("tests", "resources", "config_with_status.yaml"))
    assert config is not None
    assert status_config is None

@patch("watchmaker.utils.imds.detect.provider", return_value="unknown")
def test_config_without_status(mock_provider):
    worker_args = {
        'admin_groups': 'None',
        'admin_users': 'None',
        'computer_name': 'None',
        'salt_states': 'None',
        'ou_path': 'None'
    }
    config, status_config = get_watchmaker_configs("linux", worker_args, os.path.join("tests", "resources", "config_with_status.yaml"))
    assert config is not None
    assert status_config is None

