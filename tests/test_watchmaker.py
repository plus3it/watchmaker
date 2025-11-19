"""Watchmaker main test module."""

import platform
from pathlib import Path
from unittest.mock import patch

import pytest

import watchmaker


def test_main():
    """Placeholder for tests."""
    assert watchmaker.__version__ == watchmaker.__version__


def test_none_arguments():
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

    with patch("watchmaker.status.Status.initialize", return_value=None):
        watchmaker_client = watchmaker.Client(watchmaker_arguments)

        assert "salt_states" in watchmaker_client.worker_args
        assert watchmaker_client.worker_args["salt_states"] is None


def test_argument_default_value():
    """Ensure argument default value is `Arguments.DEFAULT_VALUE`."""
    raw_arguments = {}
    check_val = watchmaker.Arguments.DEFAULT_VALUE
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    assert watchmaker_arguments.admin_groups == check_val
    assert watchmaker_arguments.admin_users == check_val
    assert watchmaker_arguments.computer_name == check_val
    assert watchmaker_arguments.salt_states == check_val
    assert watchmaker_arguments.ou_path == check_val


def test_extra_arguments_string():
    """Test string in extra_arguments loads correctly."""
    # setup
    raw_arguments = {"extra_arguments": ["--foo", "bar"]}
    check_val = {"foo": "bar"}
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    with patch("watchmaker.status.Status.initialize", return_value=None):
        watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


def test_extra_arguments_equal_separator():
    """Test equal separator in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": [
            "--foo=bar",
        ],
    }
    check_val = {"foo": "bar"}
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    with patch("watchmaker.status.Status.initialize", return_value=None):
        watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


def test_extra_arguments_quoted_string():
    """Test quoted string in extra_arguments loads correctly."""
    # setup
    raw_arguments = {"extra_arguments": ["--foo", '"bar"']}
    check_val = {"foo": "bar"}
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    with patch("watchmaker.status.Status.initialize", return_value=None):
        watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


def test_extra_arguments_list():
    """Test list in extra_arguments loads correctly."""
    # setup
    raw_arguments = {"extra_arguments": ["--foo", '["bar"]']}
    check_val = {"foo": ["bar"]}
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    with patch("watchmaker.status.Status.initialize", return_value=None):
        watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


def test_extra_arguments_map():
    """Test map in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": [
            "--user-formulas",
            '{"foo-formula": "https://url"}',
        ],
    }
    check_val = {"user_formulas": {"foo-formula": "https://url"}}
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    with patch("watchmaker.status.Status.initialize", return_value=None):
        watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Windows prepdir test only applies on Windows",
)
def test_windows_prepdir_default():
    r"""Test that Windows prepdir resolves to C:\Watchmaker."""
    # setup
    raw_arguments = {}
    watchmaker_arguments = watchmaker.Arguments(**raw_arguments)

    # test
    with patch("watchmaker.status.Status.initialize", return_value=None):
        watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    expected_prepdir = Path("C:\\Watchmaker")
    assert watchmaker_client.system_params["prepdir"] == expected_prepdir
