# -*- coding: utf-8 -*-
"""Watchmaker main test module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import os

import pytest

from watchmaker.exceptions import WatchmakerError

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import watchmaker


def test_main():
    """Placeholder for tests."""
    assert watchmaker.__version__ == watchmaker.__version__


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_none_arguments(_provider_mock):
    """Check string 'None' conversion to None."""
    raw_arguments = {
        "admin_groups": "None",
        "admin_users": "None",
        "computer_name": "None",
        "salt_states": "None",
        "ou_path": "None",
    }
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    assert watchmaker_arguments.admin_groups is None
    assert watchmaker_arguments.admin_users is None
    assert watchmaker_arguments.computer_name is None
    assert watchmaker_arguments.salt_states is None
    assert watchmaker_arguments.ou_path is None

    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    assert "salt_states" in watchmaker_client.worker_args
    assert watchmaker_client.worker_args["salt_states"] is None


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_argument_default_value(_provider_mock):
    """Ensure argument default value is `Arguments.DEFAULT_VALUE`."""
    raw_arguments = {}
    check_val = watchmaker.Arguments.DEFAULT_VALUE
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    assert watchmaker_arguments.admin_groups == check_val
    assert watchmaker_arguments.admin_users == check_val
    assert watchmaker_arguments.computer_name == check_val
    assert watchmaker_arguments.salt_states == check_val
    assert watchmaker_arguments.ou_path == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_string(_provider_mock):
    """Test string in extra_arguments loads correctly."""
    # setup
    raw_arguments = {"extra_arguments": ["--foo", "bar"]}
    check_val = {"foo": "bar"}

    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_equal_separator(_provider_mock):
    """Test equal separator in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": [
            "--foo=bar",
        ]
    }
    check_val = {"foo": "bar"}

    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_quoted_string(_provider_mock):
    """Test quoted string in extra_arguments loads correctly."""
    # setup
    raw_arguments = {"extra_arguments": ["--foo", '"bar"']}
    check_val = {"foo": "bar"}

    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_list(_provider_mock):
    """Test list in extra_arguments loads correctly."""
    # setup
    raw_arguments = {"extra_arguments": ["--foo", '["bar"]']}
    check_val = {"foo": ["bar"]}

    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_map(_provider_mock):
    """Test map in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": ["--user-formulas", '{"foo-formula": "https://url"}']
    }
    check_val = {"user_formulas": {"foo-formula": "https://url"}}

    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_none_arguments_aws_provider(_provider_mock):
    """Check string 'None' conversion to None."""
    raw_arguments = {
        "admin_groups": "None",
        "admin_users": "None",
        "computer_name": "None",
        "salt_states": "None",
        "ou_path": "None",
    }
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    assert watchmaker_arguments.admin_groups is None
    assert watchmaker_arguments.admin_users is None
    assert watchmaker_arguments.computer_name is None
    assert watchmaker_arguments.salt_states is None
    assert watchmaker_arguments.ou_path is None

    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    assert "salt_states" in watchmaker_client.worker_args
    assert watchmaker_client.worker_args["salt_states"] is None


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_valid_name_arg_w_pattern(_provider_mock):
    """Check name matches the pattern."""
    raw_arguments = {
        "computer_name": "xyz654abcdefghe",
        "config_path": os.path.join(
            "tests", "resources", "config_with_computer_name_pattern.yaml"
        ),
    }
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    assert watchmaker_arguments.computer_name == "xyz654abcdefghe"

    watchmaker.Client(watchmaker_arguments)


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_invalid_name_arg_w_pattern(_provider_mock):
    """Check name does not match pattern."""
    raw_arguments = {
        "computer_name": "123654abcdefghlmdone",
        "config_path": os.path.join(
            "tests", "resources", "config_with_computer_name_pattern.yaml"
        ),
    }
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    assert watchmaker_arguments.computer_name == "123654abcdefghlmdone"

    with pytest.raises(WatchmakerError):
        watchmaker.Client(watchmaker_arguments)


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_valid_config_name_w_pattern(_provider_mock):
    """Check name matches the pattern."""
    raw_arguments = {
        "config_path": os.path.join(
            "tests", "resources", "config_with_computer_name_and_pattern.yaml"
        ),
    }
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    client = watchmaker.Client(watchmaker_arguments)
    assert client.config["salt"]["config"]["computer_name"] == "abc321abcdefghe"


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_name_arg_wo_pattern(_provider_mock):
    """Check name allowed without pattern."""
    raw_arguments = {
        "admin_groups": "None",
        "admin_users": "None",
        "computer_name": "123654abcdefghlmdone",
        "salt_states": "None",
        "ou_path": "None",
    }
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    assert watchmaker_arguments.computer_name == "123654abcdefghlmdone"

    watchmaker.Client(watchmaker_arguments)
