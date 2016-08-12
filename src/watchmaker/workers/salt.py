import json
import logging
import os
import shutil
import subprocess

import yaml

from watchmaker.exceptions import SystemFatal as exceptionhandler
from watchmaker.managers.base import LinuxManager, WindowsManager


class SaltLinux(LinuxManager):
    def __init__(self):
        super(SaltLinux, self).__init__()
        self.salt_conf = None
        self.config = None
        self.workingdir = None
        self.formulastoinclude = list()
        self.formulaterminationstrings = list()
        self.sourceiss3bucket = None
        self.entenv = None
        self.saltbootstrapfilename = None
        self.yum_pkgs = [
            'policycoreutils-python',
            'selinux-policy-targeted',
            'salt-minion',
        ]

        self.salt_confpath = '/etc/salt'
        self.minionconf = '/etc/salt/minion'
        self.saltcall = '/usr/bin/salt-call'
        self.saltsrv = '/srv/salt'
        self.saltfileroot = os.sep.join((self.saltsrv, 'states'))
        self.saltformularoot = os.sep.join((self.saltsrv, 'formulas'))
        self.saltpillarroot = os.sep.join((self.saltsrv, 'pillar'))
        self.saltbaseenv = os.sep.join((self.saltfileroot, 'base'))

    def _configuration_validation(self):
        if 'git' == self.config['saltinstallmethod'].lower():
            if not self.config['saltbootstrapsource']:
                logging.error(
                    'Detected `git` as the install method, but the required '
                    'parameter `saltbootstrapsource` was not provided.'
                )
            else:
                self.saltbootstrapfilename = self.config[
                    'saltbootstrapsource'].split('/')[-1]
            if not self.config['saltgitrepo']:
                logging.error(
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
                logging.debug('No salt version defined in config.')
            subprocess.call([bootstrapcmd])

    def _prepare_for_install(self):

        if self.config['formulastoinclude']:
            self.formulastoinclude = self.config['formulastoinclude']

        if self.config['formulaterminationstrings']:
            self.formulaterminationstrings = self.config[
                'formulaterminationstrings']

        self.sourceiss3bucket = self.config['sourceiss3bucket']
        self.entenv = self.config['entenv']
        self.create_working_dir('/usr/tmp/', 'saltinstall')

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

        # Download and extract any salt formulas specified in formulastoinclude
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

        file_roots = [str(self.saltbaseenv)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_conf = {
            'file_roots': {'base': file_roots},
            'pillar_roots': {'base': [str(self.saltpillarroot)]}
        }

        with open(
            os.path.join(self.salt_confpath, 'minion.d', 'watchmaker.conf'),
            'w'
        ) as f:
            yaml.dump(self.salt_conf, f, default_flow_style=False)

    def install(self, configuration, saltstates):
        """
        :param configuration:
        :param saltstates:
        :return:
        """
        try:
            self.config = json.loads(configuration)
        except ValueError:
            exceptionhandler(
                'The configuration passed was not properly formed JSON. '
                'Execution halted.'
            )

        self._configuration_validation()
        self._prepare_for_install()
        self._install_package()
        self._build_salt_formula()

        logging.info('Setting grain `systemprep`...')
        ent_env = {'enterprise_environment': str(self.entenv)}
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough', 'grains.setval',
            'systemprep', str(json.dumps(ent_env))
        ]
        self.call_process(cmd)

        if self.config['oupath']:
            print('Setting grain `join-domain`...')
            oupath = {'oupath': self.config['oupath']}
            cmd = [
                self.saltcall, '--local', '--retcode-passthrough',
                'grains.setval', '"join-domain"', json.dumps(oupath)
            ]
            self.call_process(cmd)

        print('Syncing custom salt modules...')
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough',
            'saltutil.sync_all'
        ]
        self.call_process(cmd)

        if saltstates:
            self.config['saltstates'] = saltstates
        else:
            logging.info('No command line argument to override '
                         'configuration file.')

        if 'none' == self.config['saltstates'].lower():
            print('No States were specified. Will not apply any salt states.')
        else:
            if 'highstate' == self.config['saltstates'].lower():
                logging.info(
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
                logging.info(
                    'Detected the States parameter is set to: {0}. Applying '
                    'the user-defined list of states to the system.'.format(
                        self.config['saltstates']
                    )
                )
                cmd = [
                    self.saltcall, '--local', '--retcode-passthrough',
                    'state.sls', self.config['saltstates']
                ]
                cmd.extend(self.saltcall_arguments)
                self.call_process(cmd)

        logging.info(
            'Salt states all applied successfully! '
            'Details are in the log {0}'.format(
                self.salt_results_logfile
            )
        )

        if self.workingdir:
            self.cleanup()


class SaltWindows(WindowsManager):
    def __init__(self):
        super(SaltWindows, self).__init__()
        self.installurl = None
        self.salt_conf = None
        self.config = None
        self.workingdir = None
        self.formulastoinclude = list()
        self.formulaterminationstrings = list()
        self.sourceiss3bucket = None

        self.saltroot = 'C:\\Salt'
        self.salt_confpath = 'C:\\Salt\\conf'
        self.minionconf = 'C:\\Salt\\conf\\minion'
        self.saltcall = 'C:\\Salt\\salt-call.bat'
        self.saltsrv = 'C:\\Salt\\srv'
        self.saltfileroot = os.sep.join((self.saltsrv, 'states'))
        self.saltbaseenv = os.sep.join((self.saltfileroot, 'base'))
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
            logging.error(
                'Parameter `saltinstallerurl` was not provided and is'
                ' needed for installation of Salt in Windows.'
            )

        if self.config['formulastoinclude']:
            self.formulastoinclude = self.config['formulastoinclude']

        if self.config['formulaterminationstrings']:
            self.formulaterminationstrings = self.config[
                'formulaterminationstrings']

        self.sourceiss3bucket = self.config['sourceiss3bucket']
        self.entenv = self.config['entenv']
        self.create_working_dir(
            os.path.sep.join(
                [os.environ['systemdrive'],
                 'Watchmaker',
                 'WorkingFiles']
            ),
            'Salt-'
        )

        self.salt_results_logfile = os.sep.join(
            (self.workingdir, 'saltcall.results.log')
        )
        self.salt_debug_logfile = os.sep.join(
            (self.workingdir, 'saltcall.debug.log')
        )

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
                to_directory=self.saltroot
            )

        # Download and extract any salt formulas specified in formulastoinclude
        formulas_conf = []
        for source_loc in self.formulastoinclude:
            filename = source_loc.split('/')[-1]
            file_loc = os.sep.join((self.workingdir, filename))
            self.download_file(source_loc, file_loc, self.sourceiss3bucket)
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

        file_roots = [str(self.saltbaseenv), str(self.saltwinrepo)]
        file_roots += [str(x) for x in formulas_conf]

        self.salt_conf = {
            'file_roots': {'base': file_roots},
            'pillar_roots': {'base': [str(self.saltpillarroot)]},
            'file_client': 'local',
            'winrepo_source_dir': 'salt://winrepo',
            'winrepo_dir': os.sep.join([self.saltwinrepo, 'winrepo'])
        }

        if not os.path.exists(os.path.join(self.salt_confpath, 'minion.d')):
            os.mkdir(os.path.join(self.salt_confpath, 'minion.d'))

        with open(os.path.join(self.salt_confpath,
                               'minion.d',
                               'watchmaker.conf'), "w") as f:
            yaml.dump(self.salt_conf, f, default_flow_style=False)

    def install(self, configuration, saltstates):
        """
        :param configuration:
        :param saltstates:
        :return:
        """
        try:
            self.config = json.loads(configuration)
        except ValueError:
            exceptionhandler(
                'The configuration passed was not properly formed JSON. '
                'Execution halted.'
            )

        self._prepare_for_install()
        self._install_package()
        self._build_salt_formula()

        logging.info('Setting grain `systemprep`...')
        ent_env = {'enterprise_environment': str(self.entenv)}
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough', 'grains.setval',
            'systemprep', str(json.dumps(ent_env))
        ]
        self.call_process(cmd)

        if self.config['oupath']:
            print('Setting grain `join-domain`...')
            oupath = {'oupath': self.config['oupath']}
            cmd = [
                self.saltcall, '--local', '--retcode-passthrough',
                'grains.setval', '"join-domain"', json.dumps(oupath)
            ]
            self.call_process(cmd)

        print('Syncing custom salt modules...')
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough',
            'saltutil.sync_all'
        ]
        self.call_process(cmd)

        print('Generating winrepo cache file...')
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough',
            'winrepo.genrepo'
        ]
        self.call_process(cmd)

        print('Refreshing package databse...')
        cmd = [
            self.saltcall, '--local', '--retcode-passthrough',
            'pkg.refresh_db'
        ]
        self.call_process(cmd)

        if saltstates:
            self.config['saltstates'] = saltstates
        else:
            logging.info('No command line argument to override configuration file.')

        if 'none' == self.config['saltstates'].lower():
            print('No States were specified. Will not apply any salt states.')
        else:
            if 'highstate' == self.config['saltstates'].lower():
                logging.info(
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
                logging.info(
                    'Detected the States parameter is set to: {0}. Applying '
                    'the user-defined list of states to the system.'.format(
                        self.config['saltstates']
                    )
                )
                cmd = [
                    self.saltcall, '--local', '--retcode-passthrough',
                    'state.sls', self.config['saltstates']
                ]
                cmd.extend(self.saltcall_arguments)
                self.call_process(cmd)

        logging.info(
            'Salt states all applied successfully! '
            'Details are in the log {0}'.format(
                self.salt_results_logfile
            )
        )

        if self.workingdir:
            self.cleanup()
