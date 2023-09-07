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
import re

import pytest

from watchmaker.config import get_configs, validate_computer_name_pattern
from watchmaker.exceptions import WatchmakerError

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch("watchmaker.utils.imds.detect.provider", return_value="aws")
def test_config_w_status_provider(_mock_provider):
    """Test config that has the status block and supported provider."""
    config, status_config = get_configs(
        "linux",
        {},
        os.path.join("tests", "resources", "config_with_status.yaml"),
    )
    assert config is not None
    assert status_config is not None


@patch("watchmaker.utils.imds.detect.provider", return_value="unknown")
def test_config_wo_status_config(_mock_provider):
    """Test config that does not have status block or provider."""
    config, status_config = get_configs(
        "linux",
        {},
        os.path.join("tests", "resources", "config_without_status.yaml"),
    )
    assert config is not None
    assert status_config is None


@patch("watchmaker.utils.imds.detect.provider", return_value="unknown")
def test_config_w_name_pattern(_mock_provider):
    """Test config with name pattern compare valid/invalid names."""
    valid_computer_name = "xyz654abcdefghe"
    invalid_computer_name = "123xyz654abcdefgheone"
    config, _status_config = get_configs(  # pylint: disable=unused-variable
        "linux",
        {},
        os.path.join(
            "tests", "resources", "config_with_computer_name_pattern.yaml"
        ),
    )

    pattern = config["salt"]["config"]["computer_name_pattern"]

    assert pattern == r"(?i)xyz[\d]{3}[a-z]{8}[ex]"
    assert re.match(pattern + r"\Z", valid_computer_name) is not None
    assert re.match(pattern + r"\Z", invalid_computer_name) is None

    # Test with terminal patterns and supported \Z terminal pattern combined
    dbl_terminal_pattern = "^" + pattern + r"$\Z"
    assert re.match(dbl_terminal_pattern, valid_computer_name) is not None
    assert re.match(dbl_terminal_pattern, invalid_computer_name) is None

    # Test without terminal patterns showing need for \Z
    assert re.match(pattern, valid_computer_name + "12345") is not None
    assert re.match(
        dbl_terminal_pattern,
        valid_computer_name + "12345"
    ) is None


@patch("watchmaker.utils.imds.detect.provider", return_value="unknown")
def test_config_w_name_and_pattern(_mock_provider):
    """Test config that has a pattern and computer name."""
    config, _status_config = get_configs(  # pylint: disable=unused-variable
        "linux",
        {},
        os.path.join(
            "tests", "resources", "config_with_computer_name_and_pattern.yaml"
        ),
    )
    computer_name = config["salt"]["config"]["computer_name"]
    pattern = config["salt"]["config"]["computer_name_pattern"]
    assert pattern == r"(?i)abc[\d]{3}[a-z]{8}[ex]"
    assert computer_name == "abc321abcdefghe"
    assert re.match(pattern + r"\Z", computer_name) is not None


def test_config_validate_pattern():
    """Test config validate pattern method."""
    config, _status_config = get_configs(  # pylint: disable=unused-variable
        "linux",
        {},
        os.path.join(
            "tests", "resources", "config_with_computer_name_and_pattern.yaml"
        ),
    )

    validate_computer_name_pattern(config)
    config["salt"]["config"]["computer_name_pattern"] = \
        r"?i)abc[\d]{3}[a-z]{8}[ex]"
    with pytest.raises(WatchmakerError):
        validate_computer_name_pattern(config)
