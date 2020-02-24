# -*- coding: utf-8 -*-
"""Watchmaker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os

import pytest
import yaml

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
    config_path = os.path.join(static.__path__[0], 'config.yaml')

    with open(config_path, 'r') as stream:
        return yaml.safe_load(stream)


def test_main():
    """Placeholder for tests."""
    assert watchmaker.__version__ == watchmaker.__version__


def test_none_arguments():
    """Check string 'None' conversion to None."""
    raw_arguments = {
        'admin_groups': 'None',
        'admin_users': 'None',
        'computer_name': 'None',
        'salt_states': 'None',
        'ou_path': 'None'
    }
    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    assert not watchmaker_arguments.admin_groups
    assert not watchmaker_arguments.admin_users
    assert not watchmaker_arguments.computer_name
    assert not watchmaker_arguments.salt_states
    assert not watchmaker_arguments.ou_path


def test_argument_default_value():
    """Ensure argument default value is `Arguments.DEFAULT_VALUE`."""
    raw_arguments = {}
    check_val = watchmaker.Arguments.DEFAULT_VALUE
    watchmaker_arguments = watchmaker.Arguments(**dict(**raw_arguments))

    assert watchmaker_arguments.admin_groups == check_val
    assert watchmaker_arguments.admin_users == check_val
    assert watchmaker_arguments.computer_name == check_val
    assert watchmaker_arguments.salt_states == check_val
    assert watchmaker_arguments.ou_path == check_val
