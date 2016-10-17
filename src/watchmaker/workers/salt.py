import abc
import json
import logging
import os
import shutil
import subprocess
import sys

import yaml

from watchmaker.managers.base import ManagerBase, LinuxManager, WindowsManager

lslog = logging.getLogger('LinuxSalt')
wslog = logging.getLogger('WindowsSalt')


class SaltBase(ManagerBase):
    saltbaseenv = None
    saltcall = None
    saltconfpath = None
    saltfileroot = None
    saltformularoot = None
    saltsrv = None
    saltworkingdir = None
    saltworkingdirprefix = None

    @abc.abstractmethod
    def __init__(self):
        super(SaltBase, self).__init__()
        self.config = None
        self.entenv = None
        self.formulastoinclude = list()
        self.formulaterminationstrings = list()
        self.salt_conf = None
        self.sourceiss3bucket = None
        self.workingdir = None

    @abc.abstractmethod
    def _install_package(self):
        return

    @abc.abstractmethod
    def _prepare_for_install(self):
        if self.config['formulastoinclude']:
            self.formulastoinclude = self.config['formulastoinclude']

        if self.config['formulaterminationstrings']:
            self.formulaterminationstrings = self.config[
                'formulaterminationstrings']

        self.computername = self.config['computername']
        self.entenv = self.config['entenv']
        self.sourceiss3bucket = self.config['sourceiss3bucket']

        self.create_working_dir(self.saltworkingdir, self.saltworkingdirprefix)

        self.salt_results_logfile = self.config['salt_results_log'] or \
            os.sep.join((self.workingdir, 'saltcall.results.log'))

        self.salt_debug_logfile = self.config['salt_debug_log'] or \
            os.sep.join((self.workingdir, 'saltcall.debug.log'))

        self.saltcall_arguments = [
            '--out', 'yaml', '--out-file', self.salt_results_logfile,
            '--return', 'local', '--log-file', self.salt_debug_logfile,
            '--log-file-level', 'debug'
        ]

        for saltdir in [self.saltfileroot,
                        self.saltbaseenv,
                        self.saltformularoot]:
            try:
                os.makedirs(saltdir)
            except OSError:
                if not os.path.isdir(saltdir):
                    raise

    def _get_formulas_conf(self):
        # Obtain & extract any Salt formulas specified in formulastoinclude.
        formulas_conf = []
        for source_loc in self.formulastoinclude:
            filename = source_loc.split('/')[-1]
            file_loc = os.sep.join((self.workingdir, filename))
            self.download_file(source_loc, file_loc)
            self.extract_contents(
                filepath=file_loc,
                to_directory=self.saltformularoot
            )
            filebase = '.'.join(filename.split('.')[:-1])
            formulas_loc = os.sep.join((self.saltformularoot, filebase))

            for string in self.formulaterminationstrings:
                if filebase.endswith(string):
                    newformuladir = formulas_loc[:-len(string)]
                    if os.path.exists(newformuladir):
                        shutil.rmtree(newformuladir)
                    shutil.move(formulas_loc, newformuladir)
                    formulas_loc = newformuladir
            formulas_conf.append(formulas_loc)
        return formulas_conf

    @abc.abstractmethod
    def _build_salt_formula(self):
        if self.config['saltcontentsource']:
            self.saltcontentfilename = self.config[
                'saltcontentsource'].split('/')[-1]
            self.saltcontentfile = os.sep.join((
                self.workingdir,
                self.saltcontentfilename
            ))
            self.download_file(
                self.config['saltcontentsource'],
                self.saltcontentfile,
                self.sourceiss3bucket
            )
            self.extract_contents(
                filepath=self.saltcontentfile,
                to_directory=self.saltsrv
            )

        if not os.path.exists(os.path.join(self.saltconfpath, 'minion.d')):
            os.mkdir(os.path.join(self.saltconfpath, 'minion.d'))

        with open(
            os.path.join(self.saltconfpath, 'minion.d', 'watchmaker.conf'),
            'w'
        ) as f:
            yaml.dump(self.salt_conf, f, default_flow_style=False)

    @abc.abstractmethod
    def _set_grain(self, grain, value):
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough', 'grains.setval',
            grain, str(json.dumps(value))
        ]
        self.call_process(cmd)


class SaltLinux(SaltBase, LinuxManager):
    def __init__(self):
        super(SaltLinux, self).__init__()

        # Extra variables needed for Linux.
        self.saltbootstrapfilename = None
        self.yum_pkgs = [
            'policycoreutils-python',
            'selinux-policy-targeted',
            'salt-minion',
        ]

        # Set up variables for paths to Salt directories and applications.
        self.saltcall = '/usr/bin/salt-call'
        self.saltconfpath = '/etc/salt'
        self.saltminionpath = '/etc/salt/minion'
        self.saltsrv = '/srv/salt'
        self.saltworkingdir = '/usr/tmp/'
        self.saltworkingdirprefix = 'saltinstall'

        self.saltbaseenv = os.sep.join((self.saltfileroot, 'base'))
        self.saltfileroot = os.sep.join((self.saltsrv, 'states'))
        self.saltformularoot = os.sep.join((self.saltsrv, 'formulas'))
        self.saltpillarroot = os.sep.join((self.saltsrv, 'pillar'))

    def _configuration_validation(self):
        if 'git' == self.config['saltinstallmethod'].lower():
            if not self.config['saltbootstrapsource']:
                lslog.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `saltbootstrapsource` was not provided.'
                )
            else:
                self.saltbootstrapfilename = self.config[
                    'saltbootstrapsource'].split('/')[-1]
            if not self.config['saltgitrepo']:
                lslog.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `saltgitrepo` was not provided.'
                )

    def _install_package(self):
        if 'yum' == self.config['saltinstallmethod'].lower():
            self._install_from_yum(self.yum_pkgs)
        elif 'git' == self.config['saltinstallmethod'].lower():
            self.download_file(
                self.config['saltbootstrapsource'],
                self.saltbootstrapfilename
            )
            bootstrapcmd = [
                'sh',
                self.saltbootstrapfilename,
                '-g',
                self.config['saltgitrepo']
            ]
            if self.config['saltversion']:
                bootstrapcmd.append('git')
                bootstrapcmd.append(self.config['saltversion'])
            else:
                lslog.debug('No salt version defined in config.')
            subprocess.call(bootstrapcmd)

    def _prepare_for_install(self):
        super(SaltLinux, self)._prepare_for_install()

    def _build_salt_formula(self):
        formulas_conf = super(SaltLinux, self)._get_formulas_conf()

        file_roots = [str(self.saltbaseenv)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_conf = {
            'file_client': 'local',
            'hash_type': 'sha512',
            'file_roots': {'base': file_roots},
            'pillar_roots': {'base': [str(self.saltpillarroot)]}
        }

        super(SaltLinux, self)._build_salt_formula()

    def _set_grain(self, grain, value):
        lslog.info('Setting grain `{0}` ...'.format(grain))
        super(SaltLinux, self)._set_grain(grain, value)

    def install(self, configuration, saltstates):
        """
        :param configuration:
        :param saltstates:
        :return:
        """
        try:
            self.config = json.loads(configuration)
        except ValueError:
            lslog.critical(
                'The configuration passed was not properly formed JSON. '
                'Execution halted.'
            )
            sys.exit(1)

        self._configuration_validation()
        self._prepare_for_install()
        self._install_package()
        self._build_salt_formula()

        ent_env = {'enterprise_environment': str(self.entenv)}
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

        if self.computername and self.computername != 'None':
            name = {'computername': str(self.computername)}
            self._set_grain('name-computer', name)

        print('Syncing custom salt modules...')
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough',
            'saltutil.sync_all'
        ]
        self.call_process(cmd)

        if saltstates:
            self.config['saltstates'] = saltstates
        else:
            lslog.info(
                'No command line argument to override configuration file.'
            )

        if 'none' == self.config['saltstates'].lower():
            print('No States were specified. Will not apply any salt states.')
        else:
            if 'highstate' == self.config['saltstates'].lower():
                lslog.info(
                    'Detected the States parameter is set to `highstate`. '
                    'Applying the salt `"highstate`" to the system.'
                )
                cmd = [
                    self.saltcall, '--local', '--retcode-passthrough',
                    'state.highstate'
                ]
                cmd.extend(self.saltcall_arguments)
                self.call_process(cmd)

            else:
                lslog.info(
                    'Detected the States parameter is set to: {0}. Applying '
                    'the user-defined list of states to the system.'
                    .format(self.config['saltstates'])
                )
                cmd = [
                    self.saltcall, '--local', '--retcode-passthrough',
                    'state.sls', self.config['saltstates']
                ]
                cmd.extend(self.saltcall_arguments)
                self.call_process(cmd)

        lslog.info(
            'Salt states all applied successfully! '
            'Details are in the log {0}'.format(self.salt_results_logfile)
        )

        if self.workingdir:
            self.cleanup()


class SaltWindows(SaltBase, WindowsManager):
    def __init__(self):
        super(SaltWindows, self).__init__()

        # Extra variable needed for Windows.
        self.installurl = None

        # Set up variables for paths to Salt directories and applications.
        self.saltcall = 'C:\\Salt\\salt-call.bat'
        self.saltconfpath = 'C:\\Salt\\conf'
        self.saltroot = 'C:\\Salt'
        self.saltminionpath = 'C:\\Salt\\conf\\minion'
        self.saltsrv = 'C:\\Salt\\srv'
        self.saltworkingdir = os.sep.join(
            [os.environ['systemdrive'], 'Watchmaker', 'WorkingFiles']
        )
        self.saltworkingdirprefix = 'Salt-'

        self.saltbaseenv = os.sep.join((self.saltfileroot, 'base'))
        self.saltfileroot = os.sep.join((self.saltsrv, 'states'))
        self.saltformularoot = os.sep.join((self.saltsrv, 'formulas'))
        self.saltpillarroot = os.sep.join((self.saltsrv, 'pillar'))
        self.saltwinrepo = os.sep.join((self.saltsrv, 'winrepo'))

    def _install_package(self):
        installername = self.installerurl.split('/')[-1]
        self.download_file(
            self.config['saltinstallerurl'],
            installername,
            self.sourceiss3bucket
        )
        installcmd = [
            installername,
            '/S'
        ]
        subprocess.call(installcmd)

    def _prepare_for_install(self):
        if self.config['saltinstallerurl']:
            self.installerurl = self.config['saltinstallerurl']
        else:
            wslog.error(
                'Parameter `saltinstallerurl` was not provided and is'
                ' needed for installation of Salt in Windows.'
            )

        super(SaltWindows, self)._prepare_for_install()

        # Extra Salt variable for Windows.
        self.ashrole = self.config['ashrole']

    def _build_salt_formula(self):
        formulas_conf = super(SaltWindows, self)._get_formulas_conf()

        file_roots = [str(self.saltbaseenv), str(self.saltwinrepo)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_conf = {
            'file_client': 'local',
            'hash_type': 'sha512',
            'file_roots': {'base': file_roots},
            'pillar_roots': {'base': [str(self.saltpillarroot)]},
            'winrepo_source_dir': 'salt://winrepo',
            'winrepo_dir': os.sep.join([self.saltwinrepo, 'winrepo'])
        }

        super(SaltWindows, self)._build_salt_formula()

    def _set_grain(self, grain, value):
        wslog.info('Setting grain `{0}` ...'.format(grain))
        super(SaltWindows, self)._set_grain(grain, value)

    def install(self, configuration, saltstates):
        """
        :param configuration:
        :param saltstates:
        :return:
        """
        try:
            self.config = json.loads(configuration)
        except ValueError:
            wslog.critical(
                'The configuration passed was not properly formed JSON. '
                'Execution halted.'
            )
            sys.exit(1)

        self._prepare_for_install()
        self._install_package()
        self._build_salt_formula()

        ent_env = {'enterprise_environment': str(self.entenv)}
        self._set_grain('systemprep', ent_env)

        if self.ashrole and self.ashrole != 'None':
            role = {'role': str(self.ashrole)}
            self._set_grain('ash-windows', role)

        grain = {}
        if self.config['oupath'] and self.config['oupath'] != 'None':
            grain['oupath'] = self.config['oupath']
        if self.config['admingroups'] and self.config['admingroups'] != 'None':
            grain['admingroups'] = self.config['admingroups'].split(':')
        if self.config['adminusers'] and self.config['adminusers'] != 'None':
            grain['adminusers'] = self.config['adminusers'].split(':')
        if grain:
            self._set_grain('join-domain', grain)

        if self.computername and self.computername != 'None':
            name = {'computername': str(self.computername)}
            self._set_grain('name-computer', name)

        wslog.info('Syncing custom salt modules...')
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough',
            'saltutil.sync_all'
        ]
        self.call_process(cmd)

        wslog.info('Generating winrepo cache file...')
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough',
            'winrepo.genrepo'
        ]
        self.call_process(cmd)

        wslog.info('Refreshing package database...')
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough',
            'pkg.refresh_db'
        ]
        self.call_process(cmd)

        if saltstates:
            self.config['saltstates'] = saltstates
        else:
            wslog.info(
                'No command line argument to override configuration file.'
            )

        if 'none' == self.config['saltstates'].lower():
            wslog.info(
                'No States were specified. Will not apply any salt states.'
            )
        else:
            if 'highstate' == self.config['saltstates'].lower():
                wslog.info(
                    'Detected the States parameter is set to `highstate`. '
                    'Applying the salt `"highstate`" to the system.'
                )
                cmd = [
                    self.saltcall, '--local', '--retcode-passthrough',
                    'state.highstate'
                ]
                cmd.extend(self.saltcall_arguments)
                self.call_process(cmd)

            else:
                wslog.info(
                    'Detected the States parameter is set to: {0}. Applying '
                    'the user-defined list of states to the system.'
                    .format(self.config['saltstates'])
                )
                cmd = [
                    self.saltcall, '--local', '--retcode-passthrough',
                    'state.sls', self.config['saltstates']
                ]
                cmd.extend(self.saltcall_arguments)
                self.call_process(cmd)

        wslog.info(
            'Salt states all applied successfully! '
            'Details are in the log {0}'.format(self.salt_results_logfile)
        )

        if self.workingdir:
            self.cleanup()
