# -*- coding: utf-8 -*-
"""Watchmaker main test module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import importlib_resources as resources
import pytest
import yaml

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import watchmaker
from watchmaker import static


@pytest.fixture
def watchmaker_arguments():
    """Return default watchmaker arguments."""
    watchmaker_arguments = {
        'salt_states': 'highstate',
        'no_reboot': False,
        'admin_groups': None,
        'computer_name': None,
        'admin_users': None,
        'log_level':
        'debug',
        'ou_path': None,
        'config_path': None,
        'environment': None,
        'extra_arguments': [],
        'log_dir': u'/var/log/watchmaker'
    }

    return watchmaker_arguments


@pytest.fixture
def watchmaker_client(watchmaker_arguments):
    """Return  watchmaker client with defaults."""
    return watchmaker.Client(watchmaker_arguments)


@pytest.fixture
def default_config():
    """Return default configuration for watchmaker."""
    config_path = str(resources.files(static) / 'config.yaml')

    with open(config_path, 'r') as stream:
        return yaml.safe_load(stream)


def test_main():
    """Placeholder for tests."""
    assert watchmaker.__version__ == watchmaker.__version__


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_none_arguments(provider_mock):
    """Check string 'None' conversion to None."""
    raw_arguments = {
        'admin_groups': 'None',
        'admin_users': 'None',
        'computer_name': 'None',
        'salt_states': 'None',
        'ou_path': 'None'
    }
    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    assert watchmaker_arguments.admin_groups is None
    assert watchmaker_arguments.admin_users is None
    assert watchmaker_arguments.computer_name is None
    assert watchmaker_arguments.salt_states is None
    assert watchmaker_arguments.ou_path is None

    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    assert 'salt_states' in watchmaker_client.worker_args
    assert watchmaker_client.worker_args['salt_states'] is None


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_argument_default_value(provider_mock):
    """Ensure argument default value is `Arguments.DEFAULT_VALUE`."""
    raw_arguments = {}
    check_val = watchmaker.Arguments.DEFAULT_VALUE
    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    assert watchmaker_arguments.admin_groups == check_val
    assert watchmaker_arguments.admin_users == check_val
    assert watchmaker_arguments.computer_name == check_val
    assert watchmaker_arguments.salt_states == check_val
    assert watchmaker_arguments.ou_path == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_string(provider_mock):
    """Test string in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": [
            '--foo',
            'bar'
        ]
    }
    check_val = {"foo": "bar"}

    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_equal_separator(provider_mock):
    """Test equal separator in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": [
            '--foo=bar',
        ]
    }
    check_val = {"foo": "bar"}

    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_quoted_string(provider_mock):
    """Test quoted string in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": [
            '--foo',
            '"bar"'
        ]
    }
    check_val = {"foo": "bar"}

    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_list(provider_mock):
    """Test list in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": [
            '--foo',
            '["bar"]'
        ]
    }
    check_val = {"foo": ["bar"]}

    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_extra_arguments_map(provider_mock):
    """Test map in extra_arguments loads correctly."""
    # setup
    raw_arguments = {
        "extra_arguments": [
            '--user-formulas',
            '{"foo-formula": "https://url"}'
        ]
    }
    check_val = {"user_formulas": {"foo-formula": "https://url"}}

    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    # test
    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    # assertions
    assert watchmaker_client.worker_args == check_val


@patch("watchmaker.status.Status.initialize", return_value=None)
def test_none_arguments_aws_provider(provider_mock):
    """Check string 'None' conversion to None."""
    raw_arguments = {
        'admin_groups': 'None',
        'admin_users': 'None',
        'computer_name': 'None',
        'salt_states': 'None',
        'ou_path': 'None'
    }
    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    assert watchmaker_arguments.admin_groups is None
    assert watchmaker_arguments.admin_users is None
    assert watchmaker_arguments.computer_name is None
    assert watchmaker_arguments.salt_states is None
    assert watchmaker_arguments.ou_path is None

    watchmaker_client = watchmaker.Client(watchmaker_arguments)

    assert 'salt_states' in watchmaker_client.worker_args
    assert watchmaker_client.worker_args['salt_states'] is None
