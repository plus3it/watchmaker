# -*- coding: utf-8 -*-
"""Watchmaker salt worker."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import ast
import codecs
import glob
import json
import os
import shutil

import yaml

import watchmaker.utils
from watchmaker import static
from watchmaker.exceptions import InvalidValueError, WatchmakerError
from watchmaker.managers.platform import (LinuxPlatformManager,
                                          PlatformManagerBase,
                                          WindowsPlatformManager)
from watchmaker.workers.base import WorkerBase


class SaltBase(WorkerBase, PlatformManagerBase):
    r"""
    Cross-platform worker for running salt.

    Args:
        salt_debug_log: (:obj:`list`)
            Filesystem path to a file where the salt debug output should be
            saved. When unset, the salt debug log is saved to the Watchmaker
            log directory.
            (*Default*: ``''``)

        salt_content: (:obj:`str`)
            URL to a salt content archive (zip file) that will be uncompressed
            in the watchmaker salt "srv" directory. This typically is used to
            create a top.sls file and to populate salt's file_roots.
            (*Default*: ``''``)

            - *Linux*: ``/srv/watchmaker/salt``
            - *Windows*: ``C:\Watchmaker\Salt\srv``

        salt_content_path: (:obj:`str`)
            Used in conjunction with the "salt_content" arg.
            Glob pattern for the location of salt content files inside the
            provided salt_content archive. To be used when salt content files
            are located within a sub-path of the archive, rather than at its
            top-level. Multiple paths matching the given pattern will result
            in error.
            E.g. ``salt_content_path='*/'``
            (*Default*: ``''``)

        salt_states: (:obj:`str`)
            Comma-separated string of salt states to execute. When "highstate"
            is included with additional states, "highstate" runs first, then
            the other states. Accepts two special keywords (case-insensitive):
            (*Default*: ``'highstate'``)

            - ``none``: Do not apply any salt states.
            - ``highstate``: Apply the salt "highstate".

        exclude_states: (:obj:`str`)
            Comma-separated string of states to exclude from execution.
            (*Default*: ``''``)

        user_formulas: (:obj:`dict`)
            Map of formula names and URLs to zip archives of salt formulas.
            These formulas will be downloaded, extracted, and added to the salt
            file roots. The zip archive must contain a top-level directory
            that, itself, contains the actual salt formula. To "overwrite"
            bundled submodule formulas, make sure the formula name matches the
            submodule name.
            (*Default*: ``{}``)

        admin_groups: (:obj:`str`)
            Sets a salt grain that specifies the domain groups that should have
            root privileges on Linux or admin privileges on Windows. Value must
            be a colon-separated string. E.g. ``"group1:group2"``
            (*Default*: ``''``)

        admin_users: (:obj:`str`)
            Sets a salt grain that specifies the domain users that should have
            root privileges on Linux or admin privileges on Windows. Value must
            be a colon-separated string. E.g. ``"user1:user2"``
            (*Default*: ``''``)

        environment: (:obj:`str`)
            Sets a salt grain that specifies the environment in which the
            system is being built. E.g. ``dev``, ``test``, ``prod``, etc.
            (*Default*: ``''``)

        ou_path: (:obj:`str`)
            Sets a salt grain that specifies the full DN of the OU where the
            computer account will be created when joining a domain.
            E.g. ``"OU=SuperCoolApp,DC=example,DC=com"``
            (*Default*: ``''``)

        pip_install: (:obj:`list`)
            Python packages to be installed prior to applying the high state.
            (*Default*: ``[]``)

        pip_args: (:obj:`list`)
            Options to pass to pip when installing packages.
            (*Default*: ``[]``)

        pip_index: (:obj:`str`)
            URL used for an index by pip.
            (*Default*: ``https://pypi.org/simple``)

    """

    def __init__(self, *args, **kwargs):
        # Init inherited classes
        super(SaltBase, self).__init__(*args, **kwargs)

        # Pop arguments used by SaltBase
        self.user_formulas = kwargs.pop('user_formulas', None) or {}
        self.computer_name = kwargs.pop('computer_name', None) or ''
        self.ent_env = kwargs.pop('environment', None) or ''
        self.valid_envs = kwargs.pop('valid_environments', []) or []
        self.salt_debug_log = kwargs.pop('salt_debug_log', None) or ''
        self.salt_content = kwargs.pop('salt_content', None) or ''
        self.salt_content_path = kwargs.pop('salt_content_path', None) or ''
        self.ou_path = kwargs.pop('ou_path', None) or ''
        self.admin_groups = kwargs.pop('admin_groups', None) or ''
        self.admin_users = kwargs.pop('admin_users', None) or ''
        self.pip_install = kwargs.pop('pip_install', None) or []
        self.pip_args = kwargs.pop('pip_args', None) or []
        self.pip_index = kwargs.pop('pip_index', None) or \
            'https://pypi.org/simple'
        self.salt_states = kwargs.pop('salt_states', 'highstate') or ''
        self.exclude_states = kwargs.pop('exclude_states', None) or ''

        self.computer_name = watchmaker.utils.config_none_deprecate(
            self.computer_name, self.log)
        self.salt_debug_log = watchmaker.utils.config_none_deprecate(
            self.salt_debug_log, self.log)
        self.salt_content = watchmaker.utils.config_none_deprecate(
            self.salt_content, self.log)
        self.salt_content_path = watchmaker.utils.config_none_deprecate(
            self.salt_content_path, self.log)
        self.ou_path = watchmaker.utils.config_none_deprecate(
            self.ou_path, self.log)
        self.admin_groups = watchmaker.utils.config_none_deprecate(
            self.admin_groups, self.log)
        self.admin_users = watchmaker.utils.config_none_deprecate(
            self.admin_users, self.log)
        self.salt_states = watchmaker.utils.config_none_deprecate(
            self.salt_states, self.log)

        # Init attributes used by SaltBase, overridden by inheriting classes
        self.salt_working_dir = None
        self.salt_working_dir_prefix = None
        self.salt_log_dir = None
        self.salt_conf_path = None
        self.salt_conf = None
        self.salt_call = None
        self.salt_base_env = None
        self.salt_formula_root = None
        self.salt_file_roots = None
        self.salt_state_args = None
        self.salt_debug_logfile = None

    def before_install(self):
        """Validate configuration before starting install."""
        # Convert environment to lowercase
        env = str(self.ent_env).lower()

        # Convert all valid environment to lowercase
        valid_envs = [str(x).lower() for x in self.valid_envs]

        if valid_envs and env not in valid_envs:
            msg = (
                'Selected environment ({0}) is not one of the valid'
                ' environment types: {1}'.format(env, valid_envs)
            )
            self.log.critical(msg)
            raise InvalidValueError(msg)

    def install(self):
        """Install Salt."""
        pass

    @staticmethod
    def _get_salt_dirs(srv):
        salt_base_env = os.sep.join((srv, 'states'))
        salt_formula_root = os.sep.join((srv, 'formulas'))
        salt_pillar_root = os.sep.join((srv, 'pillar'))
        return (
            salt_base_env, salt_formula_root, salt_pillar_root
        )

    def _prepare_for_install(self):
        self.working_dir = self.create_working_dir(
            self.salt_working_dir,
            self.salt_working_dir_prefix
        )

        if self.salt_debug_log:
            self.salt_debug_logfile = self.salt_debug_log
        else:
            self.salt_debug_logfile = os.sep.join(
                (self.salt_log_dir, 'salt_call.debug.log')
            )

        self.salt_state_args = [
            '--log-file', self.salt_debug_logfile,
            '--log-file-level', 'debug',
            '--log-level', 'error',
            '--out', 'quiet',
            '--return', 'local'
        ]

        for salt_dir in [
            self.salt_formula_root,
            self.salt_conf_path
        ]:
            try:
                os.makedirs(salt_dir)
            except OSError:
                if not os.path.isdir(salt_dir):
                    msg = ('Unable to create directory - {0}'.format(salt_dir))
                    self.log.error(msg)
                    raise SystemError(msg)

        with codecs.open(
            os.path.join(self.salt_conf_path, 'minion'),
            'w',
            encoding="utf-8"
        ) as fh_:
            yaml.safe_dump(self.salt_conf, fh_, default_flow_style=False)

    def _get_formulas_conf(self):

        # Append Salt formulas bundled with Watchmaker package.
        formulas_path = os.sep.join((static.__path__[0], 'salt', 'formulas'))
        for formula in os.listdir(formulas_path):
            formula_path = os.path.join(self.salt_formula_root, '', formula)
            watchmaker.utils.copytree(
                os.sep.join((formulas_path, formula)),
                formula_path,
                force=True
            )

        # Obtain & extract any Salt formulas specified in user_formulas.
        for formula_name, formula_url in self.user_formulas.items():
            filename = os.path.basename(formula_url)
            file_loc = os.sep.join((self.working_dir, filename))

            # Download the formula
            self.retrieve_file(formula_url, file_loc)

            # Extract the formula
            formula_working_dir = self.create_working_dir(
                self.working_dir,
                '{0}-'.format(filename)
            )
            self.extract_contents(
                filepath=file_loc,
                to_directory=formula_working_dir
            )

            # Get the first directory within the extracted directory
            formula_inner_dir = os.path.join(
                formula_working_dir,
                next(os.walk(formula_working_dir))[1][0]
            )

            # Move the formula to the formula root
            formula_loc = os.sep.join((self.salt_formula_root, formula_name))
            self.log.debug(
                'Placing user formula in salt file roots. formula_url=%s, '
                'formula_loc=%s',
                formula_url, formula_loc
            )
            if os.path.exists(formula_loc):
                shutil.rmtree(formula_loc)
            shutil.move(formula_inner_dir, formula_loc)

        return [
            os.path.join(self.salt_formula_root, x) for x in next(os.walk(
                self.salt_formula_root))[1]
        ]

    def _build_salt_formula(self, extract_dir):
        if self.salt_content:
            salt_content_filename = watchmaker.utils.basename_from_uri(
                self.salt_content
            )
            salt_content_file = os.sep.join((
                self.working_dir,
                salt_content_filename
            ))
            self.retrieve_file(self.salt_content, salt_content_file)
            if not self.salt_content_path:
                self.extract_contents(
                    filepath=salt_content_file,
                    to_directory=extract_dir
                )
            else:
                self.log.debug(
                    'Using salt content path: %s',
                    self.salt_content_path
                )
                temp_extract_dir = os.sep.join((
                    self.working_dir, 'salt-archive'))
                self.extract_contents(
                    filepath=salt_content_file,
                    to_directory=temp_extract_dir
                )
                salt_content_src = os.sep.join((
                    temp_extract_dir, self.salt_content_path))
                salt_content_glob = glob.glob(salt_content_src)
                self.log.debug('salt_content_glob: %s', salt_content_glob)
                if len(salt_content_glob) > 1:
                    msg = 'Found multiple paths matching' \
                          ' \'{0}\' in {1}'.format(
                              self.salt_content_path,
                              self.salt_content)
                    self.log.critical(msg)
                    raise WatchmakerError(msg)
                try:
                    salt_files_dir = salt_content_glob[0]
                except IndexError:
                    msg = 'Salt content glob path \'{0}\' not' \
                          ' found in {1}'.format(
                              self.salt_content_path,
                              self.salt_content)
                    self.log.critical(msg)
                    raise WatchmakerError(msg)

                watchmaker.utils.copy_subdirectories(
                    salt_files_dir, extract_dir, self.log)

        bundled_content = os.sep.join(
            (static.__path__[0], 'salt', 'content')
        )
        watchmaker.utils.copy_subdirectories(
            bundled_content, extract_dir, self.log)

        with codecs.open(
            os.path.join(self.salt_conf_path, 'minion'),
            'r+',
            encoding="utf-8"
        ) as fh_:
            salt_conf = yaml.safe_load(fh_)
            salt_conf.update(self.salt_file_roots)
            fh_.seek(0)
            yaml.safe_dump(salt_conf, fh_, default_flow_style=False)

    def _set_grain(self, grain, value):
        cmd = [
            'grains.setval',
            grain,
            str(json.dumps(value))
        ]
        self.run_salt(cmd)

    def _get_grain(self, grain):
        grain_full = self.run_salt(['grains.get', grain])
        return grain_full['stdout'].decode().split('\n')[1].strip()

    def _get_failed_states(self, state_ret):
        failed_states = {}
        try:
            # parse state return
            salt_id_delim = '_|-'
            salt_id_pos = 1
            for state, data in state_ret['return'].items():
                if data['result'] is False:
                    state_id = state.split(salt_id_delim)[salt_id_pos]
                    failed_states[state_id] = data
        except AttributeError:
            # some error other than a failed state, msg is in the 'return' key
            self.log.debug('Salt return (AttributeError): %s', state_ret)
            failed_states = state_ret['return']
        except KeyError:
            # not sure what failed, just return everything
            self.log.debug('Salt return (KeyError): %s', state_ret)
            failed_states = state_ret
        return failed_states

    def _install_pip(self, py_exec):
        get_pip = os.path.join(
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..')),
            'vendor',
            'pypa',
            'get-pip',
            'public',
            '2.7',
            'get-pip.py')
        self.log.info(
            'Attempting pip install using get-pip (%s)...', get_pip)
        cmd = [
            py_exec,
            get_pip,
            "--index-url",
            self.pip_index
        ]
        self.call_process(cmd)

    def _upgrade_pip(self, py_exec):
        self.log.debug('Attempting to upgrade pip...')
        cmd = [
            py_exec,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "--index-url",
            self.pip_index
        ]
        self.call_process(cmd, raise_error=False)

        ver = self.call_process([py_exec, '-m', 'pip', '--version'])
        self.log.debug('Pip version: %s', ver['stdout'])

    def _install_pip_packages(self):
        py_exec = self._get_grain('pythonexecutable')
        self.log.debug('Salt Python interpreter: `%s`', py_exec)

        try:
            ver = self.call_process([
                py_exec,
                '-m',
                'pip',
                '--version'])
            self.log.debug('Pip version: %s', ver['stdout'])
        except WatchmakerError:
            self.log.debug('Pip not installed for Salt interpreter!')
            self._install_pip(py_exec)

        self._upgrade_pip(py_exec)

        self.log.info(
            'Pip installing module(s): `%s`', " ".join(self.pip_install))
        pip_cmd = [
            py_exec,
            '-m',
            'pip',
            'install'
        ]
        pip_cmd.extend(self.pip_install)
        pip_cmd.extend(['--index-url', self.pip_index])
        pip_cmd.extend(self.pip_args)
        self.call_process(pip_cmd)

    def run_salt(self, command, **kwargs):
        """
        Execute salt command.

        Args:
            command: (:obj:`str` or :obj:`list`)
                Salt options and a salt module to be executed by salt-call.
                Watchmaker will always begin the command with the options
                ``--local``, ``--retcode-passthrough``, and ``--no-color``, so
                do not specify those options in the command.

        """
        cmd = [
            self.salt_call,
            '--local',
            '--retcode-passthrough',
            '--no-color',
            '--config-dir',
            self.salt_conf_path
        ]
        if isinstance(command, list):
            cmd.extend(command)
        else:
            cmd.append(command)

        return self.call_process(cmd, **kwargs)

    def service_status(self, service):
        """
        Get the service status using salt.

        Args:
            service: (obj:`str`)
                Name of the service to query.

        Returns:
            :obj:`tuple`: ``('running', 'enabled')``
                First element is the service running status. Second element is
                the service enabled status. Each element is a :obj:`bool`
                representing whether the service is running or enabled.

        """
        cmd_status = [
            'service.status', service,
            '--out', 'newline_values_only'
        ]
        cmd_enabled = [
            'service.enabled', service,
            '--out', 'newline_values_only'
        ]
        return (
            self.run_salt(cmd_status)['stdout'].strip().lower() == b'true',
            self.run_salt(cmd_enabled)['stdout'].strip().lower() == b'true'
        )

    def service_stop(self, service):
        """
        Stop a service status using salt.

        Args:
            service: (:obj:`str`)
                Name of the service to stop.

        Returns:
            :obj:`bool`:
                ``True`` if the service was stopped. ``False`` if the service
                could not be stopped.

        """
        cmd = [
            'service.stop', service,
            '--out', 'newline_values_only'
        ]
        return self.run_salt(cmd)['stdout'].strip().lower() == b'true'

    def service_start(self, service):
        """
        Start a service status using salt.

        Args:
            service: (:obj:`str`)
                Name of the service to start.

        Returns:
            :obj:`bool`:
                ``True`` if the service was started. ``False`` if the service
                could not be started.

        """
        cmd = [
            'service.start', service,
            '--out', 'newline_values_only'
        ]
        return self.run_salt(cmd)['stdout'].strip().lower() == b'true'

    def service_disable(self, service):
        """
        Disable a service using salt.

        Args:
            service: (:obj:`str`)
                Name of the service to disable.

        Returns:
            :obj:`bool`:
                ``True`` if the service was disabled. ``False`` if the service
                could not be disabled.

        """
        cmd = [
            'service.disable', service,
            '--out', 'newline_values_only'
        ]
        return self.run_salt(cmd)['stdout'].strip().lower() == b'true'

    def service_enable(self, service):
        """
        Enable a service using salt.

        Args:
            service: (:obj:`str`)
                Name of the service to enable.

        Returns:
            :obj:`bool`:
                ``True`` if the service was enabled. ``False`` if the service
                could not be enabled.

        """
        cmd = [
            'service.enable', service,
            '--out', 'newline_values_only'
        ]
        return self.run_salt(cmd)['stdout'].strip().lower() == b'true'

    def process_grains(self):
        """Set salt grains."""
        ent_env = {'enterprise_environment': str(self.ent_env)}
        self._set_grain('systemprep', ent_env)
        self._set_grain('watchmaker', ent_env)

        grain = {}
        if self.ou_path:
            grain['oupath'] = self.ou_path
        if self.admin_groups:
            grain['admin_groups'] = self.admin_groups.split(':')
        if self.admin_users:
            grain['admin_users'] = self.admin_users.split(':')
        if grain:
            self._set_grain('join-domain', grain)

        if self.computer_name:
            name = {'computername': str(self.computer_name)}
            self._set_grain('name-computer', name)

        self.log.info('Syncing custom salt modules...')
        self.run_salt('saltutil.sync_all')

    def process_states(self, states, exclude):
        """
        Apply salt states but exclude certain states.

        Args:
            states: (:obj:`str`)
                Comma-separated string of salt states to execute. When
                "highstate" is included with additional states, "highstate"
                runs first, then the other states. Accepts two special
                keywords (case-insensitive):

                - ``none``: Do not apply any salt states.
                - ``highstate``: Apply the salt "highstate".

            exclude: (:obj:`str`)
                Comma-separated string of states to exclude from execution.

        """
        if not states:
            self.log.info(
                'No States were specified. Will not apply any salt states.'
            )
            return

        cmds = []
        states = states.split(',')
        salt_cmd = self.salt_state_args

        highstate = False
        for state in states:
            if state.lower() == 'highstate':
                highstate = True
                states.remove(state)

        if highstate:
            self.log.info('Applying the salt "highstate"')
            cmds.append(salt_cmd + ['state.highstate'])

        if states:
            self.log.info(
                'Applying the user-defined list of states, states=%s',
                states
            )
            states = ','.join(states)
            cmds.append(salt_cmd + ['state.sls', states])

        for cmd in cmds:
            if exclude:
                cmd.extend(['exclude={0}'.format(exclude)])

            ret = self.run_salt(cmd, log_pipe='stderr', raise_error=False)

            if ret['retcode'] != 0:
                failed_states = self._get_failed_states(
                    ast.literal_eval(ret['stdout'].decode('utf-8')))
                if failed_states:
                    raise WatchmakerError(
                        yaml.safe_dump(
                            {
                                'Salt state execution failed':
                                failed_states
                            },
                            default_flow_style=False,
                            indent=4
                        )
                    )

        self.log.info('Salt states all applied successfully!')


class SaltLinux(SaltBase, LinuxPlatformManager):
    """
    Run salt on Linux.

    Args:
        install_method: (:obj:`str`)
            **Required**. Method to use to install salt.
            (*Default*: ``yum``)

            - ``yum``: Install salt from an RPM using yum.
            - ``git``: Install salt from source, using the salt bootstrap.

        bootstrap_source: (:obj:`str`)
            URL to the salt bootstrap script. Required if ``install_method`` is
            ``git``.
            (*Default*: ``''``)

        git_repo: (:obj:`str`)
            URL to the salt git repo. Required if ``install_method`` is
            ``git``.
            (*Default*: ``''``)

        salt_version: (:obj:`str`)
            A git reference present in ``git_repo``, such as a commit or a tag.
            If not specified, the HEAD of the default branch is used.
            (*Default*: ``''``)

    """

    def __init__(self, *args, **kwargs):
        # Init inherited classes
        super(SaltLinux, self).__init__(*args, **kwargs)

        # Pop arguments used by SaltLinux
        self.install_method = kwargs.pop('install_method', None) or 'yum'
        self.bootstrap_source = \
            kwargs.pop('bootstrap_source', None) or ''
        self.git_repo = kwargs.pop('git_repo', None) or ''
        self.salt_version = kwargs.pop('salt_version', None) or ''

        # Enforce lowercase and replace spaces with ^ in Linux
        if self.admin_groups:
            self.admin_groups = self.admin_groups.lower().replace(' ', '^')

        # Extra variables needed for SaltLinux.
        self.yum_pkgs = [
            'policycoreutils-python',
            'selinux-policy-targeted',
            'salt-minion',
        ]

        # Set up variables for paths to Salt directories and applications.
        self.salt_call = '/usr/bin/salt-call'
        self.salt_conf_path = '/opt/watchmaker/salt'
        self.salt_srv = '/srv/watchmaker/salt'
        self.salt_log_dir = self.system_params['logdir']
        self.salt_working_dir = self.system_params['workingdir']
        self.salt_working_dir_prefix = 'salt-'

        salt_dirs = self._get_salt_dirs(self.salt_srv)
        self.salt_base_env = salt_dirs[0]
        self.salt_formula_root = salt_dirs[1]
        self.salt_pillar_root = salt_dirs[2]

        # Set up the salt config
        self.salt_conf = {
            'file_client': 'local',
            'hash_type': 'sha512',
            'pillar_roots': {'base': [str(self.salt_pillar_root)]},
            'pillar_merge_lists': True,
            'conf_dir': self.salt_conf_path
        }

    def _configuration_validation(self):
        if self.install_method.lower() == 'git':
            if not self.bootstrap_source:
                self.log.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `bootstrap_source` was not provided.'
                )
            if not self.git_repo:
                self.log.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `git_repo` was not provided.'
                )

    def _install_package(self):
        if self.install_method.lower() == 'yum':
            self._install_from_yum(self.yum_pkgs)
        elif self.install_method.lower() == 'git':
            salt_bootstrap_filename = os.sep.join((
                self.working_dir,
                watchmaker.utils.basename_from_uri(self.bootstrap_source)
            ))
            self.retrieve_file(self.bootstrap_source, salt_bootstrap_filename)
            bootstrap_cmd = [
                'sh',
                salt_bootstrap_filename,
                '-g',
                self.git_repo
            ]
            if self.salt_version:
                bootstrap_cmd.append('git')
                bootstrap_cmd.append(self.salt_version)
            else:
                self.log.debug('No salt version defined in config.')
            self.call_process(bootstrap_cmd)

    def _build_salt_formula(self, extract_dir):
        formulas_conf = self._get_formulas_conf()

        file_roots = [str(self.salt_base_env)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_file_roots = {'file_roots': {'base': file_roots}}

        super(SaltLinux, self)._build_salt_formula(extract_dir)

    def _set_grain(self, grain, value):
        self.log.info('Setting grain `%s` ...', grain)
        super(SaltLinux, self)._set_grain(grain, value)

    def _selinux_status(self):
        selinux_getenforce = self.call_process(['getenforce'])
        return selinux_getenforce['stdout'].strip().lower() == b'enforcing'

    def _selinux_setenforce(self, state):
        return self.call_process(['setenforce', state])

    def install(self):
        """Install salt and execute salt states."""
        self._configuration_validation()
        self._prepare_for_install()

        salt_running = False
        salt_enabled = False
        salt_svc = 'salt-minion'
        if os.path.exists(self.salt_call):
            salt_running, salt_enabled = self.service_status(salt_svc)
        self._install_package()
        if self.pip_install:
            self._install_pip_packages()
        salt_stopped = self.service_stop(salt_svc)
        self._build_salt_formula(self.salt_srv)
        if salt_enabled:
            if not self.service_enable(salt_svc):
                self.log.error('Failed to enable %s service', salt_svc)
        else:
            if not self.service_disable(salt_svc):
                self.log.error('Failed to disable %s service', salt_svc)
        if salt_running and salt_stopped:
            if not self.service_start(salt_svc):
                self.log.error('Failed to restart %s service', salt_svc)

        self.process_grains()

        selinux_enforcing = self._selinux_status()
        if selinux_enforcing:
            self.log.info('Making selinux permisive for salt execution')
            self._selinux_setenforce('permissive')

        try:
            self.process_states(self.salt_states, self.exclude_states)
        finally:
            if selinux_enforcing:
                self.log.info('Setting selinux back to enforcing mode')
                self._selinux_setenforce('enforcing')

        if self.working_dir:
            self.cleanup()


class SaltWindows(SaltBase, WindowsPlatformManager):
    """
    Run salt on Windows.

    Args:
        installer_url: (:obj:`str`)
            **Required**. URL to the salt installer for Windows.
            (*Default*: ``''``)
        ash_role: (:obj:`str`)
            Sets a salt grain that specifies the role used by the ash-windows
            salt formula. E.g. ``"MemberServer"``, ``"DomainController"``, or
            ``"Workstation"``
            (*Default*: ``''``)

    """

    def __init__(self, *args, **kwargs):
        # Pop arguments used by SaltWindows
        self.installer_url = kwargs.pop('installer_url', None) or ''
        self.ash_role = kwargs.pop('ash_role', None) or ''

        # Init inherited classes
        super(SaltWindows, self).__init__(*args, **kwargs)

        self.ash_role = watchmaker.utils.config_none_deprecate(
            self.ash_role, self.log)

        # Extra variable needed for SaltWindows.
        sys_drive = os.environ['systemdrive']

        # Set up variables for paths to Salt directories and applications.
        self.salt_root = os.sep.join((sys_drive, 'Salt'))

        self.salt_call = os.sep.join((self.salt_root, 'salt-call.bat'))
        self.salt_wam_root = os.sep.join((
            self.system_params['prepdir'],
            'Salt'))
        self.salt_conf_path = os.sep.join((self.salt_wam_root, 'conf'))
        self.salt_srv = os.sep.join((self.salt_wam_root, 'srv'))
        self.salt_win_repo = os.sep.join((self.salt_srv, 'winrepo'))
        self.salt_log_dir = self.system_params['logdir']
        self.salt_working_dir = self.system_params['workingdir']
        self.salt_working_dir_prefix = 'Salt-'

        salt_dirs = self._get_salt_dirs(self.salt_srv)
        self.salt_base_env = salt_dirs[0]
        self.salt_formula_root = salt_dirs[1]
        self.salt_pillar_root = salt_dirs[2]

        # Set up the salt config
        self.salt_conf = {
            'file_client': 'local',
            'hash_type': 'sha512',
            'pillar_roots': {'base': [str(self.salt_pillar_root)]},
            'pillar_merge_lists': True,
            'conf_dir': self.salt_conf_path,
            'winrepo_source_dir': 'salt://winrepo',
            'winrepo_dir': os.sep.join((self.salt_win_repo, 'winrepo'))
        }

    def _install_package(self):
        installer_name = os.sep.join((
            self.working_dir,
            watchmaker.utils.basename_from_uri(self.installer_url)
        ))
        self.retrieve_file(self.installer_url, installer_name)
        install_cmd = [installer_name, '/S']
        self.call_process(install_cmd)

    def _prepare_for_install(self):
        if not self.installer_url:
            self.log.error(
                'Parameter `installer_url` was not provided and is'
                ' needed for installation of Salt in Windows.'
            )

        super(SaltWindows, self)._prepare_for_install()

    def _build_salt_formula(self, extract_dir):
        formulas_conf = self._get_formulas_conf()

        file_roots = [str(self.salt_base_env), str(self.salt_win_repo)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_file_roots = {'file_roots': {'base': file_roots}}

        super(SaltWindows, self)._build_salt_formula(extract_dir)

    def _set_grain(self, grain, value):
        self.log.info('Setting grain `%s` ...', grain)
        super(SaltWindows, self)._set_grain(grain, value)

    def install(self):
        """Install salt and execute salt states."""
        self._prepare_for_install()

        salt_running = False
        salt_enabled = False
        salt_svc = 'salt-minion'
        if os.path.exists(self.salt_call):
            salt_running, salt_enabled = self.service_status(salt_svc)
        self._install_package()
        if self.pip_install:
            self._install_pip_packages()
        salt_stopped = self.service_stop(salt_svc)
        self._build_salt_formula(self.salt_srv)
        if salt_enabled:
            if not self.service_enable(salt_svc):
                self.log.error('Failed to enable %s service', salt_svc)
        else:
            if not self.service_disable(salt_svc):
                self.log.error('Failed to disable %s service', salt_svc)
        if salt_running and salt_stopped:
            if not self.service_start(salt_svc):
                self.log.error('Failed to restart %s service', salt_svc)

        if self.ash_role:
            role = {'lookup': {'role': str(self.ash_role)}}
            self._set_grain('ash-windows', role)

        self.process_grains()

        self.log.info('Refreshing package database...')
        self.run_salt('pkg.refresh_db')

        self.process_states(self.salt_states, self.exclude_states)

        if self.working_dir:
            self.cleanup()
