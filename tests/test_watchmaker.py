# -*- coding: utf-8 -*-
"""Watchmaker main test module."""
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
        "extra_arguments": [
            "--user-formulas",
            '{"foo-formula": "https://url"}',
        ]
    }
    check_val = {"user_formulas": {"foo-formula": "https://url"}}

    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val
