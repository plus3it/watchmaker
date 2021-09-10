# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,protected-access
"""Salt worker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import sys

import pytest

from watchmaker.exceptions import InvalidValue
from watchmaker.workers.salt import SaltBase, SaltLinux, SaltWindows

try:
    from unittest.mock import MagicMock, call, patch
except ImportError:
    from mock import MagicMock, call, patch


@pytest.fixture
def saltworker_client():
    """Return salt worker arguments."""
    system_params = {}
    salt_config = {}

    return SaltBase(system_params, **salt_config)


@pytest.fixture
def saltworker_base_salt_args():
    """Return base arguments for salt-call."""
    return [
        '--log-file', 'salt_call.debug.log',
        '--log-file-level', 'debug',
        '--log-level', 'error',
        '--out', 'quiet',
        '--return', 'local'
    ]


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
        saltworker_client.ent_env = "bogus"
        saltworker_client.valid_envs = [None, "dev", "test", "prod"]
        saltworker_client.before_install()


def test_valid_environment(saltworker_client):
    """
    Ensure that an environment within valid_environments works as expected.

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)

    """
    saltworker_client.ent_env = "dev"
    saltworker_client.valid_envs = [None, "dev", "test", "prod"]
    assert saltworker_client.before_install() is None


def test_salt_client_defaults():
    """
    Check SaltClient default values.

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)

    """
    system_params = {}
    salt_config = {}

    saltworker_client = SaltBase(system_params, **salt_config)
    assert saltworker_client.salt_states == 'highstate'


def test_salt_client_none():
    """
    Check SaltClient handles None values properly.

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)

    """
    system_params = {}
    salt_config = {
        'salt_states': None
    }

    saltworker_client = SaltBase(system_params, **salt_config)
    assert saltworker_client.salt_states == ''


def test_salt_client_explicit_value():
    """
    Check SaltClient handles explicit values properly.

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)

    """
    system_params = {}
    salt_config = {
        'salt_states': 'foo'
    }

    saltworker_client = SaltBase(system_params, **salt_config)
    assert saltworker_client.salt_states == 'foo'


def test_process_states_highstate(
    saltworker_client,
    saltworker_base_salt_args,
):
    """
    Run process_states with "highstate".

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)

    """
    # setup
    states = 'highstate'
    exclude = None

    saltworker_client.run_salt = MagicMock(return_value={'retcode': 0})
    saltworker_client.salt_state_args = saltworker_base_salt_args

    expected = saltworker_client.salt_state_args + ['state.highstate']

    # test
    saltworker_client.process_states(states, exclude)

    # assertions
    saltworker_client.run_salt.assert_called_with(
        expected,
        log_pipe='stderr',
        raise_error=False
    )
    assert saltworker_client.run_salt.call_count == 1


def test_process_states_multiple_states(
    saltworker_client,
    saltworker_base_salt_args,
):
    """
    Run process_states with "foo,bar".

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)

    """
    # setup
    states = 'foo,bar'
    exclude = None

    saltworker_client.run_salt = MagicMock(return_value={'retcode': 0})
    saltworker_client.salt_state_args = saltworker_base_salt_args

    expected = saltworker_client.salt_state_args + ['state.sls', 'foo,bar']

    # test
    saltworker_client.process_states(states, exclude)

    # assertions
    saltworker_client.run_salt.assert_called_with(
        expected,
        log_pipe='stderr',
        raise_error=False
    )
    assert saltworker_client.run_salt.call_count == 1


def test_process_states_multiple_states_case_sensitive(
    saltworker_client,
    saltworker_base_salt_args,
):
    """
    Run process_states with "Foo,bAR".

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)

    """
    # setup
    states = 'Foo,bAR'
    exclude = None

    saltworker_client.run_salt = MagicMock(return_value={'retcode': 0})
    saltworker_client.salt_state_args = saltworker_base_salt_args

    expected = saltworker_client.salt_state_args + ['state.sls', 'Foo,bAR']

    # test
    saltworker_client.process_states(states, exclude)

    # assertions
    saltworker_client.run_salt.assert_called_with(
        expected,
        log_pipe='stderr',
        raise_error=False
    )
    assert saltworker_client.run_salt.call_count == 1


def test_process_states_highstate_extra_states(
    saltworker_client,
    saltworker_base_salt_args,
):
    """
    Run process_states with "highstate,foo,bar".

    Args:
        saltworker_client: (:obj:`src.workers.SaltBase`)

    """
    # setup
    states = 'highstate,foo,bar'
    exclude = None

    saltworker_client.run_salt = MagicMock(return_value={'retcode': 0})
    saltworker_client.salt_state_args = saltworker_base_salt_args

    call_1 = saltworker_client.salt_state_args + ['state.highstate']
    call_2 = saltworker_client.salt_state_args + ['state.sls', 'foo,bar']

    calls = [
        call(call_1, log_pipe='stderr', raise_error=False),
        call(call_2, log_pipe='stderr', raise_error=False),
    ]

    # test
    saltworker_client.process_states(states, exclude)

    # assertions
    saltworker_client.run_salt.assert_has_calls(calls)
    assert saltworker_client.run_salt.call_count == len(calls)


@patch.dict(os.environ, {"systemdrive": "C:"})
def test_windows_missing_prepdir():
    """Ensure that error raised when missing prep directory."""
    system_params = {}
    salt_config = {}

    system_params["logdir"] = "logdir"
    system_params["workingdir"] = "workingdir"

    with pytest.raises(KeyError, match="prepdir"):
        SaltWindows(system_params, **salt_config)


@patch.dict(os.environ, {"systemdrive": "C:"})
def test_windows_missing_logdir():
    """Ensure that error raised when missing log directory."""
    system_params = {}
    salt_config = {}

    system_params["prepdir"] = "prepdir"
    system_params["workingdir"] = "workingdir"

    with pytest.raises(KeyError, match="logdir"):
        SaltWindows(system_params, **salt_config)


@patch.dict(os.environ, {"systemdrive": "C:"})
def test_windows_missing_workingdir():
    """Ensure that error raised when missing working directory."""
    system_params = {}
    salt_config = {}

    system_params["logdir"] = "logdir"
    system_params["prepdir"] = "prepdir"

    with pytest.raises(KeyError, match="workingdir"):
        SaltWindows(system_params, **salt_config)


@patch.dict(os.environ, {"systemdrive": "C:"})
def test_windows_defaults():
    """Ensure that default values are populated as expected."""
    system_params = {}
    salt_config = {}

    system_params["prepdir"] = "8cbda638-6b60-5628-870b-40fdf8add9f8"
    system_params["logdir"] = "21fa57e2-9302-5934-978d-4ae40d5a2a55"
    system_params["workingdir"] = "c990ee27-ff12-5d7e-9957-1d27d114c0ff"

    salt_config["installer_url"] = "5de41ea1-902c-5e7c-ae86-89587057c6b3"
    salt_config["ash_role"] = "b116b3e1-ee3f-5a83-9dd1-3d01d0d5e343"

    win_salt = SaltWindows(system_params, **salt_config)

    # assertions ===================
    assert win_salt.installer_url == salt_config["installer_url"]
    assert win_salt.ash_role == salt_config["ash_role"]
    assert win_salt.salt_root == os.sep.join(("C:", "Salt"))
    assert win_salt.salt_call == os.sep.join(("C:", "Salt", "salt-call.bat"))
    assert win_salt.salt_wam_root == os.sep.join(
        (system_params["prepdir"], "Salt"))
    assert win_salt.salt_conf_path == os.sep.join(
        (system_params["prepdir"], "Salt", "conf")
    )
    assert win_salt.salt_srv == os.sep.join(
        (system_params["prepdir"], "Salt", "srv"))
    assert win_salt.salt_win_repo == os.sep.join(
        (system_params["prepdir"], "Salt", "srv", "winrepo")
    )
    assert win_salt.salt_log_dir == system_params["logdir"]
    assert win_salt.salt_working_dir == system_params["workingdir"]
    assert win_salt.salt_working_dir_prefix == "Salt-"

    assert win_salt.salt_base_env == os.sep.join((win_salt.salt_srv, "states"))
    assert win_salt.salt_formula_root == os.sep.join(
        (win_salt.salt_srv, "formulas"))
    assert win_salt.salt_pillar_root == os.sep.join(
        (win_salt.salt_srv, "pillar"))
    assert win_salt.salt_conf["file_client"] == "local"
    assert win_salt.salt_conf["hash_type"] == "sha512"
    assert win_salt.salt_conf["pillar_roots"] == {
        "base": [str(os.sep.join((win_salt.salt_srv, "pillar")))]
    }
    assert win_salt.salt_conf["pillar_merge_lists"]
    assert win_salt.salt_conf["conf_dir"] == os.sep.join(
        (system_params["prepdir"], "Salt", "conf")
    )
    assert win_salt.salt_conf["winrepo_source_dir"] == "salt://winrepo"
    assert win_salt.salt_conf["winrepo_dir"] == os.sep.join(
        (system_params["prepdir"], "Salt", "srv", "winrepo", "winrepo")
    )


@patch.dict(os.environ, {"systemdrive": "C:"})
def test_windows_install(saltworker_base_salt_args):
    """Ensure that install runs as expected."""
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "0dcd877d-56cb-50c2-954a-80d1084b2216"
    system_params["logdir"] = "647c2a49-baf9-511b-a17a-d6ebf0edd91c"
    system_params["workingdir"] = "3d6ab2ef-09ad-59f1-a365-ee5f22c95c79"

    salt_config["installer_url"] = "20c913cf-d825-533e-8649-4ab2fed5d9c1"
    salt_config["ash_role"] = "f1d27775-9a3d-5e87-ab42-a79ac329ae4b"

    saltworker_win = SaltWindows(system_params, **salt_config)

    saltworker_win._prepare_for_install = MagicMock(return_value=None)
    saltworker_win.salt_state_args = saltworker_base_salt_args
    saltworker_win._install_package = MagicMock(return_value=None)
    saltworker_win.service_stop = MagicMock(return_value=None)
    saltworker_win._build_salt_formula = MagicMock(return_value=None)
    saltworker_win.service_disable = MagicMock(return_value=True)
    saltworker_win._set_grain = MagicMock(return_value=None)
    saltworker_win.process_grains = MagicMock(return_value=None)
    saltworker_win.run_salt = MagicMock(return_value={"retcode": 0})
    saltworker_win.working_dir = system_params["workingdir"]
    saltworker_win.cleanup = MagicMock(return_value=None)

    run_salt_calls = [
        call("pkg.refresh_db"),
        call(
            saltworker_win.salt_state_args + ['state.highstate'],
            log_pipe='stderr',
            raise_error=False
        ),
    ]

    # test
    saltworker_win.install()

    # assertions ===================
    assert saltworker_win._prepare_for_install.call_count == 1
    assert saltworker_win._install_package.call_count == 1
    saltworker_win.service_stop.assert_called_with("salt-minion")
    saltworker_win._build_salt_formula.assert_called_with(
        saltworker_win.salt_srv)
    saltworker_win.service_disable.assert_called_with("salt-minion")
    saltworker_win._set_grain.assert_called_with(
        "ash-windows", {"lookup": {"role": salt_config["ash_role"]}}
    )
    assert saltworker_win.process_grains.call_count == 1
    assert saltworker_win.run_salt.call_count == len(run_salt_calls)
    saltworker_win.run_salt.assert_has_calls(run_salt_calls)
    assert saltworker_win.cleanup.call_count == 1


@patch.dict(os.environ, {"systemdrive": "C:"})
@patch("codecs.open", autospec=True)
@patch("os.makedirs", autospec=True)
@patch("yaml.safe_dump", autospec=True)
def test_windows_prep_install(mock_safe, mock_makedirs, mock_codec):
    """Ensure that prep portion of install runs as expected."""
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "ac2bf0c3-7985-569f-bfbd-3a8d8a13ce7d"
    system_params["logdir"] = "5b0976f8-fcbc-50af-9459-8060589e70d9"
    system_params["workingdir"] = "860f630a-f85d-5ed2-bd7a-bbdb48a53b2b"

    salt_config["installer_url"] = "5f0c8635-4a10-5802-8145-732052a0b44b"
    salt_config["ash_role"] = "fddc3dc3-3684-5924-bf55-bb1dbc4e4c08"

    saltworker_win = SaltWindows(system_params, **salt_config)

    saltworker_win.create_working_dir = MagicMock(
        return_value=system_params["workingdir"]
    )
    saltworker_win._prepare_for_install()

    # assertions ===================
    saltworker_win.create_working_dir.assert_called_with(
        system_params["workingdir"], "Salt-"
    )
    mock_makedirs.assert_called_with(saltworker_win.salt_conf_path)
    mock_codec.assert_called_with(
        os.path.join(saltworker_win.salt_conf_path, "minion"),
        "w", encoding="utf-8"
    )
    mock_safe.assert_called_with(
        saltworker_win.salt_conf,
        mock_codec.return_value.__enter__(),
        default_flow_style=False,
    )


def test_linux_computer_name_none():
    """Test that Pythonic None can be used without error rather than 'None'."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "662f1bdb-5992-5f8f-87d6-15c4de958b7b"
    system_params["logdir"] = "76b74ceb-e81d-5fac-b293-0d7d45901ef7"
    system_params["workingdir"] = "4e6a1827-1d3b-5612-a7fd-f6fed00b5a2f"

    # try "normal" first, with a value. try with none below.
    salt_config["computer_name"] = "5f0c8635-4a10-5802-8145-732052a0b44b"

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx._set_grain = MagicMock(return_value=None)
    saltworker_lx.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )

    saltworker_lx.process_grains()

    # assertions ===================
    assert saltworker_lx._set_grain.call_count == 3
    saltworker_lx._set_grain.assert_called_with(
        'name-computer', {'computername': salt_config["computer_name"]})

    # tried "normal" first, with a value, above. now, trying with none.
    salt_config["computer_name"] = None

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx._set_grain = MagicMock(return_value=None)
    saltworker_lx.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )

    saltworker_lx.process_grains()

    # assertions ===================
    assert saltworker_lx._set_grain.call_count == 2


@patch("codecs.open", autospec=True)
@patch("os.makedirs", autospec=True)
@patch("yaml.safe_dump", autospec=True)
def test_linux_salt_debug_log_none(mock_safe, mock_makedirs, mock_codec):
    """Test that Pythonic None can be used without error rather than 'None'."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "d6f194e9-7cbc-5c89-9c9c-7ad43faf8a7b"
    system_params["logdir"] = "9523029a-b7a9-50a1-83c8-d0a1b39f496f"
    system_params["workingdir"] = "f92163af-f801-5880-983a-aeb880c94a0b"

    # try "normal" first, with a value. try with none below.
    salt_config["salt_debug_log"] = "211aba6a-72f3-5659-85ce-22fc3854da2e"

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)
    saltworker_lx.create_working_dir = MagicMock(return_value=None)
    saltworker_lx._prepare_for_install()

    # assertions ===================
    assert saltworker_lx.salt_debug_logfile == salt_config["salt_debug_log"]

    # tried "normal" first, with a value, above. now, trying with none.
    salt_config["salt_debug_log"] = None

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)
    saltworker_lx.create_working_dir = MagicMock(return_value=None)
    saltworker_lx._prepare_for_install()

    # assertions ===================
    assert saltworker_lx.salt_debug_logfile == os.sep.join(
        (system_params["logdir"], 'salt_call.debug.log'))


@pytest.mark.skipif(sys.version_info < (3, 4),
                    reason="Not supported in this Python version.")
@patch("codecs.open", autospec=True)
@patch("os.walk", autospec=True)
@patch("yaml.safe_dump", autospec=True)
@patch("yaml.safe_load", autospec=True)
@patch("watchmaker.utils.copytree", autospec=True)
def test_linux_salt_content_none(
        mock_copytree, mock_yload, mock_ydump, mock_os, mock_codec):
    """Test that Pythonic None can be used without error rather than 'None'."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "1868795c-7d47-5d4d-9021-941b449967af"
    system_params["logdir"] = "e88611fe-d444-5951-bb20-4d7508ed7a0c"
    system_params["workingdir"] = "f671935d-6669-50d1-a63c-157799cd13cb"

    salt_config["salt_content"] = None

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx.retrieve_file = MagicMock(return_value=None)
    saltworker_lx.extract_contents = MagicMock(return_value=None)

    saltworker_lx._build_salt_formula("c6295b26-c043-5cd8-aa83-e3aab9df263c")

    # assertions ===================
    assert saltworker_lx.retrieve_file.call_count == 0
    assert saltworker_lx.extract_contents.call_count == 0
    assert mock_codec.call_count == 1
    assert mock_os.call_count == 2
    assert mock_ydump.call_count == 1
    assert mock_yload.call_count == 1
    assert mock_copytree.call_count > 1


@pytest.mark.skipif(sys.version_info < (3, 4),
                    reason="Not supported in this Python version.")
@patch("codecs.open", autospec=True)
@patch("os.walk", autospec=True)
@patch("yaml.safe_dump", autospec=True)
@patch("yaml.safe_load", autospec=True)
@patch("watchmaker.utils.copytree", autospec=True)
@patch("glob.glob", autospec=True)
@patch("watchmaker.utils.copy_subdirectories", autospec=True)
def test_linux_salt_content_path_none(
        mock_copysubdirs, mock_glob, mock_copytree, mock_yload,
        mock_ydump, mock_os, mock_codec):
    """Test that Pythonic None can be used without error rather than 'None'."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "4504257a-76d0-49bd-9d04-53c1459b7156"
    system_params["logdir"] = "045143d6-0e87-497f-a11a-5eebb1ec7edf"
    system_params["workingdir"] = "83f16e7b-c2cf-482b-93c8-32a558f6ded6"

    salt_config["salt_content"] = "33691f8e-e245-4be2-827b-2fa727600fb4.zip"
    salt_config["salt_content_path"] = None

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)
    saltworker_lx.working_dir = system_params["workingdir"]

    saltworker_lx.retrieve_file = MagicMock(return_value=None)
    saltworker_lx.extract_contents = MagicMock(return_value=None)

    saltworker_lx._build_salt_formula("e8d7398e-49fa-4eb9-8f8b-22c9d3fdb7f7")

    # assertions ===================
    assert saltworker_lx.retrieve_file.call_count == 1
    assert saltworker_lx.extract_contents.call_count == 1
    assert mock_copysubdirs.call_count == 1
    assert mock_codec.call_count == 1
    assert mock_os.call_count == 1
    assert mock_ydump.call_count == 1
    assert mock_yload.call_count == 1
    assert mock_copytree.call_count > 1
    assert mock_glob.call_count == 0


@pytest.mark.skipif(sys.version_info < (3, 4),
                    reason="Not supported in this Python version.")
@patch("codecs.open", autospec=True)
@patch("os.walk", autospec=True)
@patch("yaml.safe_dump", autospec=True)
@patch("yaml.safe_load", autospec=True)
@patch("watchmaker.utils.copytree", autospec=True)
@patch("glob.glob", autospec=True)
def test_linux_salt_content_path(
        mock_glob, mock_copytree, mock_yload,
        mock_ydump, mock_os, mock_codec):
    """Ensure that files from salt_content_path are retrieved correctly."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "96003f32-5808-4ef8-a573-763b7f47ba9d"
    system_params["logdir"] = "0585f9d7-ed0e-4a1b-ac0d-2b10a245a0eb"
    system_params["workingdir"] = "35f411db-355b-4953-ae31-d6f592753e58"

    salt_config["salt_content"] = "d002be6e-645d-4f58-97c9-8335df0ff5e4.zip"
    salt_config["salt_content_path"] = "05628e08-f1be-474d-8c12-5bb6517fc5f9"

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx.retrieve_file = MagicMock(return_value=None)
    saltworker_lx.extract_contents = MagicMock(return_value=None)
    saltworker_lx.working_dir = system_params["workingdir"]
    mock_glob.return_value = ['05628e08-f1be-474d-8c12-5bb6517fc5f9/87a2324d']

    saltworker_lx._build_salt_formula("8822e968-deea-410f-9b6e-d25a36c512d1")

    # assertions ===================
    assert saltworker_lx.retrieve_file.call_count == 1
    assert saltworker_lx.extract_contents.call_count == 1
    assert mock_codec.call_count == 1
    assert mock_os.call_count == 3
    assert mock_ydump.call_count == 1
    assert mock_yload.call_count == 1
    assert mock_copytree.call_count > 1
    assert mock_glob.call_count == 1


def test_linux_ou_path_none():
    """Test that Pythonic None can be used without error rather than 'None'."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "dba0f4db-3851-54b0-b2f7-bfff6bb8bbf5"
    system_params["logdir"] = "f9d62bf8-7ffe-58a8-9ad9-2d21a430e52b"
    system_params["workingdir"] = "0a5e5983-3d95-58b3-92a8-c4673902b47d"

    # try "normal" first, with a value. try with none below.
    salt_config["ou_path"] = "b547b63d-31e8-50b0-a97f-761ac8279319"

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx._set_grain = MagicMock(return_value=None)
    saltworker_lx.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )

    saltworker_lx.process_grains()

    # assertions ===================
    assert saltworker_lx._set_grain.call_count == 3
    saltworker_lx._set_grain.assert_called_with(
        'join-domain', {'oupath': salt_config["ou_path"]})

    # tried "normal" first, with a value, above. now, trying with none.
    salt_config["ou_path"] = None

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx._set_grain = MagicMock(return_value=None)
    saltworker_lx.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )

    saltworker_lx.process_grains()

    # assertions ===================
    assert saltworker_lx._set_grain.call_count == 2


def test_linux_admin_groups_none():
    """Test that Pythonic None can be used without error rather than 'None'."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "a27f71e5-4af3-5ad4-9d69-05fb8b7cbe4f"
    system_params["logdir"] = "9b504864-814c-5226-9a05-b7613dd96efa"
    system_params["workingdir"] = "d468d406-1e89-5041-9900-0a9189e541b0"

    # try "normal" first, with a value. try with none below.
    salt_config["admin_groups"] = "5a8915b6-8ceb-53c8-a9c6-064365dd10bd"

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx._set_grain = MagicMock(return_value=None)
    saltworker_lx.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )

    saltworker_lx.process_grains()

    # assertions ===================
    assert saltworker_lx._set_grain.call_count == 3
    saltworker_lx._set_grain.assert_called_with(
        'join-domain', {'admin_groups': [salt_config["admin_groups"]]})

    # tried "normal" first, with a value, above. now, trying with none.
    salt_config["admin_groups"] = None

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx._set_grain = MagicMock(return_value=None)
    saltworker_lx.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )

    saltworker_lx.process_grains()

    # assertions ===================
    assert saltworker_lx._set_grain.call_count == 2


def test_linux_admin_users_none():
    """Test that Pythonic None can be used without error rather than 'None'."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "ff7b4ffb-99a0-50c2-af78-98ebfea33295"
    system_params["logdir"] = "3744bc20-0357-50f1-8633-178151d904ab"
    system_params["workingdir"] = "455feea8-481c-5014-8a7b-cdeb619a2177"

    # try "normal" first, with a value. try with none below.
    salt_config["admin_users"] = "3113d136-bfde-5bc4-bc47-855d72d58d29"

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx._set_grain = MagicMock(return_value=None)
    saltworker_lx.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )

    saltworker_lx.process_grains()

    # assertions ===================
    assert saltworker_lx._set_grain.call_count == 3
    saltworker_lx._set_grain.assert_called_with(
        'join-domain', {'admin_users': [salt_config["admin_users"]]})

    # tried "normal" first, with a value, above. now, trying with none.
    salt_config["admin_users"] = None

    # execution ====================
    saltworker_lx = SaltLinux(system_params, **salt_config)

    saltworker_lx._set_grain = MagicMock(return_value=None)
    saltworker_lx.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )

    saltworker_lx.process_grains()

    # assertions ===================
    assert saltworker_lx._set_grain.call_count == 2


@patch.dict(os.environ, {"systemdrive": "C:"})
def test_win_ash_role_none():
    """Test that Pythonic None can be used without error rather than 'None'."""
    # setup ========================
    system_params = {}
    salt_config = {}
    system_params["prepdir"] = "4e91a26a-c325-5548-9e99-e0cea505eca6"
    system_params["logdir"] = "1a74aa66-1eb5-5f6e-bbdc-a247cfabdcb7"
    system_params["workingdir"] = "3cbd1221-01f3-5ed8-8df1-79918a1ebe3d"

    # try "normal" first, with a value. try with none below.
    salt_config["ash_role"] = "ff059d6b-b614-5b55-8b94-4d29570b8da8"

    saltworker_win = SaltWindows(system_params, **salt_config)

    saltworker_win.working_dir = system_params["workingdir"]
    saltworker_win._prepare_for_install = MagicMock(return_value=None)
    saltworker_win.service_status = MagicMock(return_value=None)
    saltworker_win._install_package = MagicMock(return_value=None)
    saltworker_win.service_stop = MagicMock(return_value=None)
    saltworker_win._build_salt_formula = MagicMock(return_value=None)
    saltworker_win.service_enable = MagicMock(return_value=None)
    saltworker_win.service_disable = MagicMock(return_value=None)
    saltworker_win.service_start = MagicMock(return_value=None)
    saltworker_win._set_grain = MagicMock(return_value=None)
    saltworker_win.process_grains = MagicMock(return_value=None)
    saltworker_win.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )
    saltworker_win.process_states = MagicMock(return_value=None)
    saltworker_win.cleanup = MagicMock(return_value=None)

    # execution ====================
    saltworker_win.install()

    # assertions ===================
    assert saltworker_win._set_grain.call_count == 1
    saltworker_win._set_grain.assert_called_with(
        'ash-windows', {'lookup': {'role': salt_config["ash_role"]}})

    # tried "normal" first, with a value, above. now, trying with none.
    salt_config["ash_role"] = None

    saltworker_win = SaltWindows(system_params, **salt_config)

    saltworker_win.working_dir = system_params["workingdir"]
    saltworker_win._prepare_for_install = MagicMock(return_value=None)
    saltworker_win.service_status = MagicMock(return_value=None)
    saltworker_win._install_package = MagicMock(return_value=None)
    saltworker_win.service_stop = MagicMock(return_value=None)
    saltworker_win._build_salt_formula = MagicMock(return_value=None)
    saltworker_win.service_enable = MagicMock(return_value=None)
    saltworker_win.service_disable = MagicMock(return_value=None)
    saltworker_win.service_start = MagicMock(return_value=None)
    saltworker_win._set_grain = MagicMock(return_value=None)
    saltworker_win.process_grains = MagicMock(return_value=None)
    saltworker_win.run_salt = MagicMock(
        return_value={"retcode": 0, "stdout": b"", "stderr": b""}
    )
    saltworker_win.process_states = MagicMock(return_value=None)
    saltworker_win.cleanup = MagicMock(return_value=None)

    # execution ====================
    saltworker_win.install()

    # assertions ===================
    assert saltworker_win._set_grain.call_count == 0
