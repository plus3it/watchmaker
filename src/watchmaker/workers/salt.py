import json
import logging
import os
import shutil
import subprocess
import sys

import yaml

from watchmaker import static
from watchmaker.managers.base import LinuxManager, ManagerBase, WindowsManager

ls_log = logging.getLogger('LinuxSalt')
ws_log = logging.getLogger('WindowsSalt')


class SaltBase(ManagerBase):
    salt_base_env = None
    salt_call = None
    salt_conf_path = None
    salt_file_root = None
    salt_formula_root = None
    salt_srv = None
    salt_log_dir = None
    salt_working_dir = None
    salt_working_dir_prefix = None

    def __init__(self):
        super(SaltBase, self).__init__()
        self.config = None
        self.ent_env = None
        self.formula_termination_strings = list()
        self.formulas_to_include = list()
        self.is_s3_bucket = None
        self.salt_conf = None
        self.working_dir = None

    def _set_salt_dirs(self, srv):
        self.salt_file_root = os.sep.join((srv, 'states'))
        self.salt_base_env = os.sep.join((self.salt_file_root, 'base'))
        self.salt_formula_root = os.sep.join((srv, 'formulas'))
        self.salt_pillar_root = os.sep.join((srv, 'pillar'))

    def _prepare_for_install(self, this_log):
        if self.config['user_formulas']:
            self.formulas_to_include = self.config['user_formulas']

        if self.config['formulaterminationstrings']:
            self.formula_termination_strings = self.config[
                'formulaterminationstrings']

        self.computer_name = self.config['computername']
        self.ent_env = self.config['entenv']
        if not self.is_s3_bucket:
            self.is_s3_bucket = self.config['sourceiss3bucket']

        self.create_working_dir(
            self.salt_working_dir,
            self.salt_working_dir_prefix
        )

        self.salt_results_logfile = self.config['salt_results_log'] or \
            os.sep.join((self.salt_log_dir, 'salt_call.results.log'))

        self.salt_debug_logfile = self.config['salt_debug_log'] or \
            os.sep.join((self.salt_log_dir, 'salt_call.debug.log'))

        self.salt_call_args = [
            '--out', 'yaml', '--out-file', self.salt_results_logfile,
            '--return', 'local', '--log-file', self.salt_debug_logfile,
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
                    this_log.error(msg)
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
        if self.config['saltcontentsource']:
            self.salt_content_filename = self.config[
                'saltcontentsource'].split('/')[-1]
            self.salt_content_file = os.sep.join((
                self.working_dir,
                self.salt_content_filename
            ))
            self.download_file(
                self.config['saltcontentsource'],
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
            self.salt_call, '--local', '--retcode-passthrough',
            'grains.setval', grain, str(json.dumps(value))
        ]
        self.call_process(cmd)

    def run_salt(self, command):
        cmd = [self.salt_call, '--local', '--retcode-passthrough']
        if isinstance(command, list):
            cmd.extend(command)
        else:
            cmd.append(command)
        self.call_process(cmd)

    def load_config(self, configuration, this_log):
        try:
            self.config = json.loads(configuration)
        except ValueError:
            this_log.critical(
                'The configuration passed was not properly formed JSON. '
                'Execution halted.'
            )
            sys.exit(1)

    def process_grains(self, this_log):
        ent_env = {'enterprise_environment': str(self.ent_env)}
        self._set_grain('systemprep', ent_env)

        grain = {}
        if self.config['oupath'] and self.config['oupath'] != 'None':
            grain['oupath'] = self.config['oupath']
        if self.config['admingroups'] and self.config['admingroups'] != 'None':
            grain['admingroups'] = self.config['admingroups'].split(':')
        if self.config['adminusers'] and self.config['adminusers'] != 'None':
            grain['adminusers'] = self.config['adminusers'].split(':')
        if grain:
            self._set_grain('join-domain', grain)

        if self.computer_name and self.computer_name != 'None':
            name = {'computer_name': str(self.computer_name)}
            self._set_grain('name-computer', name)

        this_log.info('Syncing custom salt modules...')
        self.run_salt('saltutil.sync_all')

    def process_states(self, states, this_log):
        if states:
            self.config['saltstates'] = states
        else:
            this_log.info(
                'No command line argument to override configuration file.'
            )

        if 'none' == self.config['saltstates'].lower():
            this_log.info(
                'No States were specified. Will not apply any salt states.'
            )
        else:
            if 'highstate' == self.config['saltstates'].lower():
                this_log.info(
                    'Detected the States parameter is set to `highstate`. '
                    'Applying the salt `"highstate`" to the system.'
                )
                cmd = ['state.highstate']
                cmd.extend(self.salt_call_args)
                self.run_salt(cmd)

            else:
                this_log.info(
                    'Detected the States parameter is set to: {0}. Applying '
                    'the user-defined list of states to the system.'
                    .format(self.config['salt_states'])
                )
                cmd = ['state.sls', self.config['saltstates']]
                cmd.extend(self.salt_call_args)
                self.run_salt(cmd)

        this_log.info(
            'Salt states all applied successfully! '
            'Details are in the log {0}'.format(self.salt_results_logfile)
        )


class SaltLinux(SaltBase, LinuxManager):
    def __init__(self):
        super(SaltLinux, self).__init__()

        # Extra variables needed for Linux.
        self.salt_bootstrap_filename = None
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
        self.salt_log_dir = '/var/log/'
        self.salt_working_dir = '/usr/tmp/'
        self.salt_working_dir_prefix = 'saltinstall'

        self._set_salt_dirs(self.salt_srv)

    def _configuration_validation(self):
        if 'git' == self.config['saltinstallmethod'].lower():
            if not self.config['saltbootstrapsource']:
                ls_log.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `saltbootstrapsource` was not provided.'
                )
            else:
                self.salt_bootstrap_filename = self.config[
                    'saltbootstrapsource'].split('/')[-1]
            if not self.config['saltgitrepo']:
                ls_log.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `saltgitrepo` was not provided.'
                )

    def _install_package(self):
        if 'yum' == self.config['saltinstallmethod'].lower():
            self._install_from_yum(self.yum_pkgs)
        elif 'git' == self.config['saltinstallmethod'].lower():
            self.download_file(
                self.config['saltbootstrapsource'],
                self.salt_bootstrap_filename
            )
            bootstrap_cmd = [
                'sh',
                self.salt_bootstrap_filename,
                '-g',
                self.config['saltgitrepo']
            ]
            if self.config['saltversion']:
                bootstrap_cmd.append('git')
                bootstrap_cmd.append(self.config['saltversion'])
            else:
                ls_log.debug('No salt version defined in config.')
            subprocess.call(bootstrap_cmd)

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
        ls_log.info('Setting grain `{0}` ...'.format(grain))
        super(SaltLinux, self)._set_grain(grain, value)

    def install(self, configuration, is_s3_bucket, salt_states):
        self.load_config(configuration, ls_log)
        self.is_s3_bucket = is_s3_bucket

        self._configuration_validation()
        self._prepare_for_install(ls_log)
        self._install_package()
        self._build_salt_formula()

        self.process_grains(ls_log)
        self.process_states(salt_states, ls_log)

        if self.working_dir:
            self.cleanup()


class SaltWindows(SaltBase, WindowsManager):
    def __init__(self):
        super(SaltWindows, self).__init__()

        # Extra variable needed for Windows.
        self.install_url = None

        sys_drive = os.environ['systemdrive']

        # Set up variables for paths to Salt directories and applications.
        self.salt_root = os.sep.join((sys_drive, 'Salt'))

        self.salt_call = os.sep.join((self.salt_root, 'salt-call.bat'))
        self.salt_conf_path = os.sep.join((self.salt_root, 'conf'))
        self.salt_min_path = os.sep.join((self.salt_root, 'minion'))
        self.salt_srv = os.sep.join((self.salt_root, 'srv'))
        self.salt_win_repo = os.sep.join((self.salt_srv, 'winrepo'))
        self.salt_log_dir = os.sep.join((sys_drive, 'Watchmaker', 'Logs'))
        self.salt_working_dir = os.sep.join(
            (sys_drive, 'Watchmaker', 'WorkingFiles')
        )
        self.salt_working_dir_prefix = 'Salt-'

        self._set_salt_dirs(self.salt_srv)

    def _install_package(self):
        installer_name = self.installerurl.split('/')[-1]
        self.download_file(
            self.config['saltinstallerurl'],
            installer_name,
            self.is_s3_bucket
        )
        install_cmd = [
            installer_name,
            '/S'
        ]
        subprocess.call(install_cmd)

    def _prepare_for_install(self):
        if self.config['saltinstallerurl']:
            self.installerurl = self.config['saltinstallerurl']
        else:
            ws_log.error(
                'Parameter `saltinstallerurl` was not provided and is'
                ' needed for installation of Salt in Windows.'
            )

        super(SaltWindows, self)._prepare_for_install(ws_log)

        # Extra Salt variable for Windows.
        self.ash_role = self.config['ashrole']

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
        ws_log.info('Setting grain `{0}` ...'.format(grain))
        super(SaltWindows, self)._set_grain(grain, value)

    def install(self, configuration, is_s3_bucket, salt_states):
        self.load_config(configuration, ws_log)
        self.is_s3_bucket = is_s3_bucket

        self._prepare_for_install()
        self._install_package()
        self._build_salt_formula()

        if self.ash_role and self.ash_role != 'None':
            role = {'role': str(self.ash_role)}
            self._set_grain('ash-windows', role)

        self.process_grains(ws_log)

        ws_log.info('Generating winrepo cache file...')
        self.run_salt('winrepo.genrepo')
        ws_log.info('Refreshing package database...')
        self.run_salt('pkg.refresh_db')

        self.process_states(salt_states, ws_log)

        if self.working_dir:
            self.cleanup()
