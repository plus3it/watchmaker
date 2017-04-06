# -*- coding: utf-8 -*-
"""Watchmaker salt worker."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import codecs
import json
import os
import shutil

import yaml

from watchmaker import static
from watchmaker.managers.base import LinuxManager, ManagerBase, WindowsManager


class SaltBase(ManagerBase):
    r"""
    Cross-platform worker for running salt.

    Args:
        salt_debug_log (:obj:`list`):
            (Defaults to ``''``) Filesystem path to a file where the salt debug
            output should be saved. When unset, the salt debug log is saved to
            the Watchmaker log directory.
        s3_source (:obj:`bool`):
            (Defaults to ``False``) Use S3 utilities to download salt content
            and user formulas from an S3 bucket. If ``True``, you must also
            install ``boto3`` and ``botocore``. Those dependencies will not be
            installed by Watchmaker.
        salt_content (:obj:`str`):
            (Defaults to ``''``) URL to a salt content archive (zip file) that
            will be uncompressed in the salt "srv" directory. This typically is
            used to create a top.sls file and to populate salt's file_roots.

            - *Linux*: ``/srv/salt``
            - *Windows*: ``C:\Salt\srv``

        salt_states (:obj:`str`):
            (Defaults to ``''``) Comma-separated string of salt states to
            execute. Accepts two special keywords (case-insensitive):

            - ``none``: Do not apply any salt states.
            - ``highstate``: Apply the salt "highstate".

        user_formulas (:obj:`dict`):
            (Defaults to ``{}``) Map of formula names and URLs to zip archives
            of salt formulas. These formulas will be downloaded, extracted, and
            added to the salt file roots. The zip archive must contain a
            top-level directory that, itself, contains the actual salt formula.
            To "overwrite" bundled submodule formulas, make sure the formula
            name matches the submodule name.
        admin_groups (:obj:`str`):
            (Defaults to ``''``) Sets a salt grain that specifies the domain
            groups that should have root privileges on Linux or admin
            privileges on Windows. Value must be a colon-separated string.
            E.g. ``"group1:group2"``
        admin_users (:obj:`str`):
            (Defaults to ``''``) Sets a salt grain that specifies the domain
            users that should have root privileges on Linux or admin
            privileges on Windows. Value must be a colon-separated string.
            E.g. ``"user1:user2"``
        environment (:obj:`str`):
            (Defaults to ``''``) Sets a salt grain that specifies the
            environment in which the system is being built. E.g. ``dev``,
            ``test``, ``prod``, etc.
        ou_path (:obj:`str`):
            (Defaults to ``''``) Sets a salt grain that specifies the full DN
            of the OU where the computer account will be created when joining a
            domain. E.g. ``"OU=SuperCoolApp,DC=example,DC=com"``
    """

    def __init__(self, *args, **kwargs):  # noqa: D102
        # Init inherited classes
        super(SaltBase, self).__init__(*args, **kwargs)

        # Pop arguments used by SaltBase
        self.user_formulas = kwargs.pop('user_formulas', None) or {}
        self.computer_name = kwargs.pop('computer_name', None) or ''
        self.ent_env = kwargs.pop('environment', None) or ''
        self.s3_source = kwargs.pop('s3_source', None) or False
        self.salt_debug_log = kwargs.pop('salt_debug_log', None) or ''
        self.salt_content = kwargs.pop('salt_content', None) or ''
        self.ou_path = kwargs.pop('ou_path', None) or ''
        self.admin_groups = kwargs.pop('admin_groups', None) or ''
        self.admin_users = kwargs.pop('admin_users', None) or ''
        self.salt_states = kwargs.pop('salt_states', None) or ''

        # Init attributes used by SaltBase, overridden by inheriting classes
        self.salt_working_dir = None
        self.salt_working_dir_prefix = None
        self.salt_log_dir = None
        self.salt_conf_path = None
        self.salt_conf = None
        self.salt_call = None
        self.salt_base_env = None
        self.salt_formula_root = None
        self.salt_call_args = None
        self.salt_debug_logfile = None

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

        if (
            self.salt_debug_log and
            self.salt_debug_log != 'None'
        ):
            self.salt_debug_logfile = self.salt_debug_log
        else:
            self.salt_debug_logfile = os.sep.join(
                (self.salt_log_dir, 'salt_call.debug.log')
            )

        self.salt_call_args = [
            '--log-file', self.salt_debug_logfile,
            '--log-file-level', 'debug',
            '--state-output', 'mixed_id'
        ]

        for salt_dir in [
            self.salt_base_env,
            self.salt_formula_root
        ]:
            try:
                os.makedirs(salt_dir)
            except OSError:
                if not os.path.isdir(salt_dir):
                    msg = ('Unable create directory - {0}'.format(salt_dir))
                    self.log.error(msg)
                    raise SystemError(msg)

    def _get_formulas_conf(self):

        # Append Salt formulas bundled with Watchmaker package.
        formulas_path = os.sep.join((static.__path__[0], 'salt', 'formulas'))
        for formula in os.listdir(formulas_path):
            formula_path = os.path.join(self.salt_formula_root, '', formula)
            if os.path.exists(formula_path):
                shutil.rmtree(formula_path)
            shutil.copytree(
                os.sep.join((formulas_path, formula)),
                formula_path)

        # Obtain & extract any Salt formulas specified in user_formulas.
        for formula_name, formula_url in self.user_formulas.items():
            filename = os.path.basename(formula_url)
            file_loc = os.sep.join((self.working_dir, filename))

            # Download the formula
            self.download_file(formula_url, file_loc)

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
            salt_content_filename = self.salt_content.split('/')[-1]
            salt_content_file = os.sep.join((
                self.working_dir,
                salt_content_filename
            ))
            self.download_file(
                self.salt_content,
                salt_content_file,
                self.s3_source
            )
            self.extract_contents(
                filepath=salt_content_file,
                to_directory=extract_dir
            )

        if not os.path.exists(os.path.join(self.salt_conf_path, 'minion.d')):
            os.mkdir(os.path.join(self.salt_conf_path, 'minion.d'))

        with codecs.open(
            os.path.join(self.salt_conf_path, 'minion.d', 'watchmaker.conf'),
            'w',
            encoding="utf-8"
        ) as fh_:
            yaml.safe_dump(self.salt_conf, fh_, default_flow_style=False)

    def _set_grain(self, grain, value):
        cmd = [
            'grains.setval',
            grain,
            str(json.dumps(value))
        ]
        self.run_salt(cmd)

    def run_salt(self, command, stdout=False):
        """
        Execute salt command.

        Args:
            command (str or list):
                Salt options and a salt module to be executed by salt-call.
                Watchmaker will always begin the command with the options
                ``--local``, ``--retcode-passthrough``, and ``--no-color``, so
                do not specify those options in the command.
            stdout (obj:`bool`) Switch to control whether to return stdout.
        """
        cmd = [
            self.salt_call,
            '--local',
            '--retcode-passthrough',
            '--no-color'
        ]
        if isinstance(command, list):
            cmd.extend(command)
        else:
            cmd.append(command)
        ret = self.call_process(cmd, stdout=stdout)
        if stdout:
            return ret

    def get_service_status(self, service):
        """
        Get the service status using salt.

        Args:
            service (obj:`str`): Name of the service to query.

        Returns:
            obj:`bool`. ``True`` if the service is running. ``False`` if the
            service is not running or not present.
        """
        cmd = [
            'service.status', service,
            '--out', 'newline_values_only'
        ]
        ret = self.run_salt(cmd, stdout=True)
        return ret.strip().lower() == b'true'

    def stop_service(self, service):
        """
        Stop a service status using salt.

        Args:
            service (obj:`str`): Name of the service to stop.

        Returns:
            obj:`bool`. ``True`` if the service was stopped. ``False`` if the
            service could not be stopped.
        """
        cmd = [
            'service.stop', service,
            '--out', 'newline_values_only'
        ]
        ret = self.run_salt(cmd, stdout=True)
        return ret.strip().lower() == b'true'

    def start_service(self, service):
        """
        Start a service status using salt.

        Args:
            service (obj:`str`): Name of the service to start.

        Returns:
            obj:`bool`. ``True`` if the service was started. ``False`` if the
            service could not be started.
        """
        cmd = [
            'service.start', service,
            '--out', 'newline_values_only'
        ]
        ret = self.run_salt(cmd, stdout=True)
        return ret.strip().lower() == b'true'

    def process_grains(self):
        """Set salt grains."""
        ent_env = {'enterprise_environment': str(self.ent_env)}
        self._set_grain('systemprep', ent_env)

        grain = {}
        if self.ou_path and self.ou_path != 'None':
            grain['oupath'] = self.ou_path
        if self.admin_groups and self.admin_groups != 'None':
            grain['admingroups'] = self.admin_groups.split(':')
        if self.admin_users and self.admin_users != 'None':
            grain['adminusers'] = self.admin_users.split(':')
        if grain:
            self._set_grain('join-domain', grain)

        if self.computer_name and self.computer_name != 'None':
            name = {'computer_name': str(self.computer_name)}
            self._set_grain('name-computer', name)

        self.log.info('Syncing custom salt modules...')
        self.run_salt('saltutil.sync_all')

    def process_states(self, states):
        """
        Apply salt states.

        Args:
            states (:obj:`str`):
                Comma-separated string of salt states to execute. Accepts two
                special keywords (case-insensitive):

                - ``none``: Do not apply any salt states.
                - ``highstate``: Apply the salt "highstate".

        """
        if not states or states.lower() == 'none':
            self.log.info(
                'No States were specified. Will not apply any salt states.'
            )
        elif states.lower() == 'highstate':
            self.log.info(
                'Detected the `states` parameter is set to `highstate`. '
                'Applying the salt "highstate" to the system.'
            )
            cmd = ['state.highstate']
            cmd.extend(self.salt_call_args)
            self.run_salt(cmd)
        else:
            self.log.info(
                'Detected the `states` parameter is set to: `%s`. Applying '
                'the user-defined list of states to the system.',
                states
            )
            cmd = ['state.sls', states]
            cmd.extend(self.salt_call_args)
            self.run_salt(cmd)

        self.log.info('Salt states all applied successfully!')


class SaltLinux(SaltBase, LinuxManager):
    """
    Run salt on Linux.

    Args:
        install_method (:obj:`str`):
            (Defaults to ``yum``) Method to use to install salt.

            - ``yum``: Install salt from an RPM using yum.
            - ``git``: Install salt from source, using the salt bootstrap.

        bootstrap_source (:obj:`str`):
            (Defaults to ``''``) URL to the salt bootstrap script. Required if
            ``install_method`` is ``git``.
        git_repo (:obj:`str`):
            (Defaults to ``''``) URL to the salt git repo. Required if
            ``install_method`` is ``git``.
        salt_version (:obj:`str`):
            (Defaults to ``''``) A git reference present in ``git_repo``, such
            as a commit or a tag. If not specified, the HEAD of the default
            branch is used.
    """

    def __init__(self, *args, **kwargs):  # noqa: D102
        # Init inherited classes
        super(SaltLinux, self).__init__(*args, **kwargs)

        # Pop arguments used by SaltLinux
        self.install_method = kwargs.pop('install_method', None) or 'yum'
        self.bootstrap_source = \
            kwargs.pop('bootstrap_source', None) or ''
        self.git_repo = kwargs.pop('git_repo', None) or ''
        self.salt_version = kwargs.pop('salt_version', None) or ''

        # Extra variables needed for SaltLinux.
        self.yum_pkgs = [
            'policycoreutils-python',
            'selinux-policy-targeted',
            'salt-minion',
        ]

        # Set up variables for paths to Salt directories and applications.
        self.salt_call = '/usr/bin/salt-call'
        self.salt_conf_path = '/etc/salt'
        self.salt_min_path = '/etc/salt/minion'
        self.salt_srv = '/srv/salt'
        self.salt_log_dir = self.system_params['logdir']
        self.salt_working_dir = self.system_params['workingdir']
        self.salt_working_dir_prefix = 'salt-'

        salt_dirs = self._get_salt_dirs(self.salt_srv)
        self.salt_base_env = salt_dirs[0]
        self.salt_formula_root = salt_dirs[1]
        self.salt_pillar_root = salt_dirs[2]

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
                self.bootstrap_source.split('/')[-1]
            ))
            self.download_file(
                self.bootstrap_source,
                salt_bootstrap_filename
            )
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

    def _build_salt_formula(self, srv):
        formulas_conf = self._get_formulas_conf()

        file_roots = [str(self.salt_base_env)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_conf = {
            'file_client': 'local',
            'hash_type': 'sha512',
            'file_roots': {'base': file_roots},
            'pillar_roots': {'base': [str(self.salt_pillar_root)]}
        }

        super(SaltLinux, self)._build_salt_formula(srv)

    def _set_grain(self, grain, value):
        self.log.info('Setting grain `%s` ...', grain)
        super(SaltLinux, self)._set_grain(grain, value)

    def install(self):
        """Install salt and execute salt states."""
        self._configuration_validation()
        self._prepare_for_install()

        status_salt = False
        if os.path.exists(self.salt_call):
            status_salt = self.get_service_status('salt-minion')
        self._install_package()
        stopped_salt = self.stop_service('salt-minion')
        self._build_salt_formula(self.salt_srv)
        if status_salt and stopped_salt:
            started_salt = self.start_service('salt-minion')
            if not started_salt:
                self.log.error('Failed to restart salt-minion service')

        self.process_grains()
        self.process_states(self.salt_states)

        if self.working_dir:
            self.cleanup()


class SaltWindows(SaltBase, WindowsManager):
    """
    Run salt on Windows.

    Args:
        installer_url (:obj:`str`):
            (Defaults to ``''``) Required. URL to the salt installer for
            Windows.
        ash_role (:obj:`str`):
            (Defaults to ``''``) Sets a salt grain that specifies the role
            used by the ash-windows salt formula. E.g. ``"MemberServer"``,
            ``"DomainController"``, or ``"Workstation"``
    """

    def __init__(self, *args, **kwargs):  # noqa: D102
        # Pop arguments used by SaltWindows
        self.installer_url = kwargs.pop('installer_url', None) or ''
        self.ash_role = kwargs.pop('ash_role', None) or ''

        # Init inherited classes
        super(SaltWindows, self).__init__(*args, **kwargs)

        # Extra variable needed for SaltWindows.
        sys_drive = os.environ['systemdrive']

        # Set up variables for paths to Salt directories and applications.
        self.salt_root = os.sep.join((sys_drive, 'Salt'))

        self.salt_call = os.sep.join((self.salt_root, 'salt-call.bat'))
        self.salt_conf_path = os.sep.join((self.salt_root, 'conf'))
        self.salt_min_path = os.sep.join((self.salt_root, 'minion'))
        self.salt_srv = os.sep.join((self.salt_root, 'srv'))
        self.salt_win_repo = os.sep.join((self.salt_srv, 'winrepo'))
        self.salt_log_dir = self.system_params['logdir']
        self.salt_working_dir = self.system_params['workingdir']
        self.salt_working_dir_prefix = 'Salt-'

        salt_dirs = self._get_salt_dirs(self.salt_srv)
        self.salt_base_env = salt_dirs[0]
        self.salt_formula_root = salt_dirs[1]
        self.salt_pillar_root = salt_dirs[2]

    def _install_package(self):
        installer_name = os.sep.join(
            (self.working_dir, self.installer_url.split('/')[-1])
        )
        self.download_file(
            self.installer_url,
            installer_name,
            self.s3_source
        )
        install_cmd = [installer_name, '/S']
        self.call_process(install_cmd)

    def _prepare_for_install(self):
        if not self.installer_url:
            self.log.error(
                'Parameter `installer_url` was not provided and is'
                ' needed for installation of Salt in Windows.'
            )

        super(SaltWindows, self)._prepare_for_install()

    def _build_salt_formula(self, root):
        formulas_conf = self._get_formulas_conf()

        file_roots = [str(self.salt_base_env), str(self.salt_win_repo)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_conf = {
            'file_client': 'local',
            'hash_type': 'sha512',
            'file_roots': {'base': file_roots},
            'pillar_roots': {'base': [str(self.salt_pillar_root)]},
            'winrepo_source_dir': 'salt://winrepo',
            'winrepo_dir': os.sep.join((self.salt_win_repo, 'winrepo'))
        }

        super(SaltWindows, self)._build_salt_formula(root)

    def _set_grain(self, grain, value):
        self.log.info('Setting grain `%s` ...', grain)
        super(SaltWindows, self)._set_grain(grain, value)

    def install(self):
        """Install salt and execute salt states."""
        self._prepare_for_install()

        status_salt = False
        if os.path.exists(self.salt_call):
            status_salt = self.get_service_status('salt-minion')
        self._install_package()
        stopped_salt = self.stop_service('salt-minion')
        self._build_salt_formula(self.salt_srv)
        if status_salt and stopped_salt:
            started_salt = self.start_service('salt-minion')
            if not started_salt:
                self.log.error('Failed to restart salt-minion service')

        if self.ash_role and self.ash_role != 'None':
            role = {'role': str(self.ash_role)}
            self._set_grain('ash-windows', role)

        self.process_grains()

        self.log.info('Generating winrepo cache file...')
        self.run_salt('winrepo.genrepo')
        self.log.info('Refreshing package database...')
        self.run_salt('pkg.refresh_db')

        self.process_states(self.salt_states)

        if self.working_dir:
            self.cleanup()
