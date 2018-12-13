# -*- coding: utf-8 -*-
"""Salt worker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import pytest

from watchmaker.exceptions import InvalidValue
from watchmaker.workers.salt import SaltBase


@pytest.fixture
def saltworker_client():
    """Return salt worker arguments."""
    system_params = {}
    salt_config = {}

    return SaltBase(system_params, **salt_config)


def test_default_valid_environments(saltworker_client):
    """
    Ensure valid_environment checks work as expected.

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)
    """
    # test that the defaults work
    assert saltworker_client.before_install() is None


def test_bogus_environment(saltworker_client):
    """
    Ensure a bogus environment throws InvalidValue.

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)
    """
    # ensure InvalidValue is raised when a bogus environment type is selected
    with pytest.raises(InvalidValue):
        saltworker_client.ent_env = 'bogus'
        saltworker_client.valid_envs = [None, 'dev', 'test', 'prod']
        saltworker_client.before_install()


def test_valid_environment(saltworker_client):
    """
    Ensure that an environment within valid_environments works as expected.

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)
    """
    saltworker_client.ent_env = 'dev'
    saltworker_client.valid_envs = [None, 'dev', 'test', 'prod']
    assert saltworker_client.before_install() is None
