# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,protected-access
"""Salt worker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os

import pytest

from watchmaker.exceptions import InvalidValue
from watchmaker.workers.salt import SaltBase, SaltWindows

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


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


@patch.dict(os.environ, {'systemdrive': 'C:'})
def test_windows_missing_prepdir():
    """Ensure that error raised when missing prep directory."""
    system_params = {}
    salt_config = {}

    system_params['logdir'] = "logdir"
    system_params['workingdir'] = "workingdir"

    with pytest.raises(KeyError, match='prepdir'):
        SaltWindows(system_params, **salt_config)


@patch.dict(os.environ, {'systemdrive': 'C:'})
def test_windows_missing_logdir():
    """Ensure that error raised when missing log directory."""
    system_params = {}
    salt_config = {}

    system_params['prepdir'] = "prepdir"
    system_params['workingdir'] = "workingdir"

    with pytest.raises(KeyError, match='logdir'):
        SaltWindows(system_params, **salt_config)


@patch.dict(os.environ, {'systemdrive': 'C:'})
def test_windows_missing_workingdir():
    """Ensure that error raised when missing working directory."""
    system_params = {}
    salt_config = {}

    system_params['logdir'] = "logdir"
    system_params['prepdir'] = "prepdir"

    with pytest.raises(KeyError, match='workingdir'):
        SaltWindows(system_params, **salt_config)


@patch.dict(os.environ, {'systemdrive': 'C:'})
def test_windows_defaults():
    """Ensure that default values are populated as expected."""
    system_params = {}
    salt_config = {}

    system_params['prepdir'] = "8cbda638-6b60-5628-870b-40fdf8add9f8"
    system_params['logdir'] = "21fa57e2-9302-5934-978d-4ae40d5a2a55"
    system_params['workingdir'] = "c990ee27-ff12-5d7e-9957-1d27d114c0ff"

    salt_config['installer_url'] = "5de41ea1-902c-5e7c-ae86-89587057c6b3"
    salt_config['ash_role'] = "b116b3e1-ee3f-5a83-9dd1-3d01d0d5e343"

    win_salt = SaltWindows(system_params, **salt_config)

    # assertions ===================
    assert win_salt.installer_url == salt_config['installer_url']
    assert win_salt.ash_role == salt_config['ash_role']
    assert win_salt.salt_root == os.sep.join(("C:", 'Salt'))
    assert win_salt.salt_call == os.sep.join(("C:", 'Salt', 'salt-call.bat'))
    assert win_salt.salt_wam_root == os.sep.join((
        system_params['prepdir'],
        'Salt',
    ))
    assert win_salt.salt_conf_path == os.sep.join((
        system_params['prepdir'],
        'Salt',
        'conf',
    ))
    assert win_salt.salt_srv == os.sep.join((
        system_params['prepdir'],
        'Salt',
        'srv',
    ))
    assert win_salt.salt_win_repo == os.sep.join((
        system_params['prepdir'],
        'Salt',
        'srv',
        'winrepo',
    ))
    assert win_salt.salt_log_dir == system_params['logdir']
    assert win_salt.salt_working_dir == system_params['workingdir']
    assert win_salt.salt_working_dir_prefix == 'Salt-'

    assert win_salt.salt_base_env == os.sep.join((
        win_salt.salt_srv,
        'states'
    ))
    assert win_salt.salt_formula_root == os.sep.join((
        win_salt.salt_srv,
        'formulas'
    ))
    assert win_salt.salt_pillar_root == os.sep.join((
        win_salt.salt_srv,
        'pillar'
    ))
    assert win_salt.salt_conf['file_client'] == 'local'
    assert win_salt.salt_conf['hash_type'] == 'sha512'
    assert win_salt.salt_conf['pillar_roots'] == {'base': [str(os.sep.join((
        win_salt.salt_srv,
        'pillar'
    )))]}
    assert win_salt.salt_conf['pillar_merge_lists']
    assert win_salt.salt_conf['conf_dir'] == os.sep.join((
        system_params['prepdir'],
        'Salt',
        'conf',
    ))
    assert win_salt.salt_conf['winrepo_source_dir'] == 'salt://winrepo'
    assert win_salt.salt_conf['winrepo_dir'] == os.sep.join((
        system_params['prepdir'],
        'Salt',
        'srv',
        'winrepo',
        'winrepo',
    ))


@patch.dict(os.environ, {'systemdrive': 'C:'})
def test_windows_install():
    """Ensure that install runs as expected."""
    system_params = {}
    salt_config = {}
    system_params['prepdir'] = "0dcd877d-56cb-50c2-954a-80d1084b2216"
    system_params['logdir'] = "647c2a49-baf9-511b-a17a-d6ebf0edd91c"
    system_params['workingdir'] = "3d6ab2ef-09ad-59f1-a365-ee5f22c95c79"

    salt_config['installer_url'] = "20c913cf-d825-533e-8649-4ab2fed5d9c1"
    salt_config['ash_role'] = "f1d27775-9a3d-5e87-ab42-a79ac329ae4b"

    saltworker_win = SaltWindows(system_params, **salt_config)

    saltworker_win._prepare_for_install = MagicMock(return_value=None)
    saltworker_win._install_package = MagicMock(return_value=None)
    saltworker_win.service_stop = MagicMock(return_value=None)
    saltworker_win._build_salt_formula = MagicMock(return_value=None)
    saltworker_win.service_disable = MagicMock(return_value=True)
    saltworker_win._set_grain = MagicMock(return_value=None)
    saltworker_win.process_grains = MagicMock(return_value=None)
    saltworker_win.run_salt = MagicMock(return_value=None)
    saltworker_win.working_dir = system_params['workingdir']
    saltworker_win.cleanup = MagicMock(return_value=None)

    saltworker_win.install()

    # assertions ===================
    assert saltworker_win._prepare_for_install.call_count == 1
    assert saltworker_win._install_package.call_count == 1
    saltworker_win.service_stop.assert_called_with('salt-minion')
    saltworker_win._build_salt_formula.assert_called_with(
        saltworker_win.salt_srv
    )
    saltworker_win.service_disable.assert_called_with('salt-minion')
    saltworker_win._set_grain.assert_called_with(
        'ash-windows', {'lookup': {'role': salt_config['ash_role']}}
    )
    assert saltworker_win.process_grains.call_count == 1
    saltworker_win.run_salt.assert_called_with('pkg.refresh_db')
    assert saltworker_win.cleanup.call_count == 1


@patch.dict(os.environ, {'systemdrive': 'C:'})
@patch('codecs.open', autospec=True)
@patch('os.makedirs', autospec=True)
@patch('yaml.safe_dump', autospec=True)
def test_windows_prep_install(mock_safe, mock_makedirs, mock_codec):
    """Ensure that prep portion of install runs as expected."""
    system_params = {}
    salt_config = {}
    system_params['prepdir'] = "ac2bf0c3-7985-569f-bfbd-3a8d8a13ce7d"
    system_params['logdir'] = "5b0976f8-fcbc-50af-9459-8060589e70d9"
    system_params['workingdir'] = "860f630a-f85d-5ed2-bd7a-bbdb48a53b2b"

    salt_config['installer_url'] = "5f0c8635-4a10-5802-8145-732052a0b44b"
    salt_config['ash_role'] = "fddc3dc3-3684-5924-bf55-bb1dbc4e4c08"

    saltworker_win = SaltWindows(system_params, **salt_config)

    saltworker_win.create_working_dir = MagicMock(
        return_value=system_params['workingdir']
    )
    saltworker_win._prepare_for_install()

    # assertions ===================
    saltworker_win.create_working_dir.assert_called_with(
        system_params['workingdir'],
        'Salt-'
    )
    mock_makedirs.assert_called_with(saltworker_win.salt_conf_path)
    mock_codec.assert_called_with(
        os.path.join(saltworker_win.salt_conf_path, 'minion'),
        'w',
        encoding="utf-8"
    )
    mock_safe.assert_called_with(
        saltworker_win.salt_conf,
        mock_codec.return_value.__enter__(),
        default_flow_style=False
    )
