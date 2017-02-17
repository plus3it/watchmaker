# -*- coding: utf-8 -*-
"""Watchmaker salt worker."""
import json
import os
import shutil

import yaml

from watchmaker import static
from watchmaker.managers.base import LinuxManager, ManagerBase, WindowsManager


class SaltBase(ManagerBase):
    """Cross-platform worker for running salt."""

    def __init__(self, *args, **kwargs):  # noqa: D102
        # Pop arguments used by SaltBase
        self.formulas_to_include = kwargs.pop('user_formulas', None) or []
        self.formula_termination_strings = \
            kwargs.pop('formulaterminationstrings', None) or []
        self.computer_name = kwargs.pop('computername', None) or ''
        self.ent_env = kwargs.pop('entenv', None) or ''
        self.is_s3_bucket = kwargs.pop('sourceiss3bucket', None) or False
        self.salt_debug_log = kwargs.pop('salt_debug_log', None) or ''
        self.saltcontentsource = kwargs.pop('saltcontentsource', None) or ''
        self.oupath = kwargs.pop('oupath', None) or ''
        self.admingroups = kwargs.pop('admingroups', None) or ''
        self.adminusers = kwargs.pop('adminusers', None) or ''
        self.saltstates = kwargs.pop('saltstates', None) or ''

        # Init inherited classes
        super(SaltBase, self).__init__(*args, **kwargs)

    def _set_salt_dirs(self, srv):
        self.salt_file_root = os.sep.join((srv, 'states'))
        self.salt_base_env = os.sep.join((self.salt_file_root, 'base'))
        self.salt_formula_root = os.sep.join((srv, 'formulas'))
        self.salt_pillar_root = os.sep.join((srv, 'pillar'))

    def _prepare_for_install(self):
        self.create_working_dir(
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
            '--log-file-level', 'debug'
        ]

        for salt_dir in [
            self.salt_file_root,
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
        formulas = {}

        # Append Salt formulas that came with Watchmaker package.
        formulas_path = os.sep.join((static.__path__[0], 'salt', 'formulas'))
        for formula in os.listdir(formulas_path):
            static_path = os.sep.join((formulas_path, formula))
            if os.path.isdir(static_path) and os.listdir(static_path):
                formulas[formula] = static_path

        # Obtain & extract any Salt formulas specified in user_formulas.
        for source_loc in self.formulas_to_include:
            filename = source_loc.split('/')[-1]
            file_loc = os.sep.join((self.working_dir, filename))
            self.download_file(source_loc, file_loc)
            self.extract_contents(
                filepath=file_loc,
                to_directory=self.salt_formula_root
            )
            filebase = '.'.join(filename.split('.')[:-1])
            formula_loc = os.sep.join((self.salt_formula_root, filebase))

            for string in self.formula_termination_strings:
                if filebase.endswith(string):
                    new_formula_dir = formula_loc[:-len(string)]
                    if os.path.exists(new_formula_dir):
                        shutil.rmtree(new_formula_dir)
                    shutil.move(formula_loc, new_formula_dir)
                    formula_loc = new_formula_dir

            formulas[filename] = formula_loc

        return formulas.values()

    def _build_salt_formula(self, extract_dir):
        if self.saltcontentsource:
            self.salt_content_filename = self.saltcontentsource.split('/')[-1]
            self.salt_content_file = os.sep.join((
                self.working_dir,
                self.salt_content_filename
            ))
            self.download_file(
                self.saltcontentsource,
                self.salt_content_file,
                self.is_s3_bucket
            )
            self.extract_contents(
                filepath=self.salt_content_file,
                to_directory=extract_dir
            )

        if not os.path.exists(os.path.join(self.salt_conf_path, 'minion.d')):
            os.mkdir(os.path.join(self.salt_conf_path, 'minion.d'))

        with open(
            os.path.join(self.salt_conf_path, 'minion.d', 'watchmaker.conf'),
            'w'
        ) as f:
            yaml.dump(self.salt_conf, f, default_flow_style=False)

    def _set_grain(self, grain, value):
        cmd = [
            'grains.setval',
            grain,
            str(json.dumps(value))
        ]
        self.run_salt(cmd)

    def run_salt(self, command):
        """
        Execute salt command.

        Args:
            command(str or list):
                Salt options and a salt module to be executed by salt-call.
                Watchmaker will always begin the command with the options
                ``--local``, ``--retcode-passthrough``, and ``--no-color``, so
                do not specify those options in the command.
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
        self.call_process(cmd)

    def process_grains(self):
        """Set salt grains."""
        ent_env = {'enterprise_environment': str(self.ent_env)}
        self._set_grain('systemprep', ent_env)

        grain = {}
        if self.oupath and self.oupath != 'None':
            grain['oupath'] = self.oupath
        if self.admingroups and self.admingroups != 'None':
            grain['admingroups'] = self.admingroups.split(':')
        if self.adminusers and self.adminusers != 'None':
            grain['adminusers'] = self.adminusers.split(':')
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
                special keywords:

                - ``'none'``: Do not apply any salt states
                - ``'highstate'``: Apply the salt highstate
        """
        if not states or states.lower() == 'none':
            self.log.info(
                'No States were specified. Will not apply any salt states.'
            )
        elif states.lower() == 'highstate':
            self.log.info(
                'Detected the `states` parameter is set to `highstate`. '
                'Applying the salt `"highstate`" to the system.'
            )
            cmd = ['state.highstate']
            cmd.extend(self.salt_call_args)
            self.run_salt(cmd)
        else:
            self.log.info(
                'Detected the `states` parameter is set to: `{0}`. Applying '
                'the user-defined list of states to the system.'
                .format(states)
            )
            cmd = ['state.sls', states]
            cmd.extend(self.salt_call_args)
            self.run_salt(cmd)

        self.log.info('Salt states all applied successfully!')


class SaltLinux(SaltBase, LinuxManager):
    """Run salt on Linux."""

    def __init__(self, *args, **kwargs):  # noqa: D102
        # Pop arguments used by SaltLinux
        self.saltinstallmethod = kwargs.pop('saltinstallmethod', None) or 'yum'
        self.saltbootstrapsource = \
            kwargs.pop('saltbootstrapsource', None) or ''
        self.saltgitrepo = kwargs.pop('saltgitrepo', None) or ''
        self.saltversion = kwargs.pop('saltversion', None) or ''

        # Init inherited classes
        super(SaltLinux, self).__init__(*args, **kwargs)

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

        self._set_salt_dirs(self.salt_srv)

    def _configuration_validation(self):
        if 'git' == self.saltinstallmethod.lower():
            if not self.saltbootstrapsource:
                self.log.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `saltbootstrapsource` was not provided.'
                )
            else:
                self.salt_bootstrap_filename = \
                    self.saltbootstrapsource.split('/')[-1]
            if not self.saltgitrepo:
                self.log.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `saltgitrepo` was not provided.'
                )

    def _install_package(self):
        if 'yum' == self.saltinstallmethod.lower():
            self._install_from_yum(self.yum_pkgs)
        elif 'git' == self.saltinstallmethod.lower():
            self.download_file(
                self.saltbootstrapsource,
                self.salt_bootstrap_filename
            )
            bootstrap_cmd = [
                'sh',
                self.salt_bootstrap_filename,
                '-g',
                self.saltgitrepo
            ]
            if self.saltversion:
                bootstrap_cmd.append('git')
                bootstrap_cmd.append(self.saltversion)
            else:
                self.log.debug('No salt version defined in config.')
            self.call_process(bootstrap_cmd)

    def _build_salt_formula(self):
        formulas_conf = self._get_formulas_conf()

        file_roots = [str(self.salt_base_env)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_conf = {
            'file_client': 'local',
            'hash_type': 'sha512',
            'file_roots': {'base': file_roots},
            'pillar_roots': {'base': [str(self.salt_pillar_root)]}
        }

        super(SaltLinux, self)._build_salt_formula(self.salt_srv)

    def _set_grain(self, grain, value):
        self.log.info('Setting grain `{0}` ...'.format(grain))
        super(SaltLinux, self)._set_grain(grain, value)

    def install(self):
        """Install salt and execute salt states."""
        self._configuration_validation()
        self._prepare_for_install()
        self._install_package()
        self._build_salt_formula()

        self.process_grains()
        self.process_states(self.saltstates)

        if self.working_dir:
            self.cleanup()


class SaltWindows(SaltBase, WindowsManager):
    """Run salt on Windows."""

    def __init__(self, *args, **kwargs):  # noqa: D102
        # Pop arguments used by SaltWindows
        self.installerurl = kwargs.pop('saltinstallerurl', None) or ''
        self.ash_role = kwargs.pop('ashrole', None) or ''

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

        self._set_salt_dirs(self.salt_srv)

    def _install_package(self):
        installer_name = os.sep.join(
            (self.working_dir, self.installerurl.split('/')[-1])
        )
        self.download_file(
            self.installerurl,
            installer_name,
            self.is_s3_bucket
        )
        install_cmd = [installer_name, '/S']
        self.call_process(install_cmd)

    def _prepare_for_install(self):
        if not self.installerurl:
            self.log.error(
                'Parameter `saltinstallerurl` was not provided and is'
                ' needed for installation of Salt in Windows.'
            )

        super(SaltWindows, self)._prepare_for_install()

    def _build_salt_formula(self):
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

        super(SaltWindows, self)._build_salt_formula(self.salt_root)

    def _set_grain(self, grain, value):
        self.log.info('Setting grain `{0}` ...'.format(grain))
        super(SaltWindows, self)._set_grain(grain, value)

    def install(self):
        """Install salt and execute salt states."""
        self._prepare_for_install()
        self._install_package()
        self._build_salt_formula()

        if self.ash_role and self.ash_role != 'None':
            role = {'role': str(self.ash_role)}
            self._set_grain('ash-windows', role)

        self.process_grains()

        self.log.info('Generating winrepo cache file...')
        self.run_salt('winrepo.genrepo')
        self.log.info('Refreshing package database...')
        self.run_salt('pkg.refresh_db')

        self.process_states(self.saltstates)

        if self.working_dir:
            self.cleanup()
