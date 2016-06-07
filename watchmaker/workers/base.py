import os
import re
import sys
import json
import yaml
import shutil
import logging
import subprocess

from watchmaker.managers.base import LinuxManager
from watchmaker.exceptions import SystemFatal as exceptionhandler


class Yum(LinuxManager):
    """
    Yum worker class.  This class handles linux distro validation and repo installation.
    """

    def __init__(self):
        """
        Instatiates the class.
        """
        super(Yum, self).__init__()
        self.dist = None
        self.version = None
        self.epel_version = None

    def _validate_distro(self):
        """
        Private method for validating the linux distrbution uses yum and is configurable.
        """

        self.dist = None
        self.version = None
        self.epel_version = None

        supported_dists = ('amazon', 'centos', 'red hat')

        match_supported_dist = re.compile(r"^({0})"
                                          "(?:[^0-9]+)"
                                          "([\d]+[.][\d]+)"
                                          "(?:.*)"
                                          .format('|'.join(supported_dists)))
        amazon_epel_versions = {
            '2014.03': '6',
            '2014.09': '6',
            '2015.03': '6',
            '2015.09': '6',
        }

        # Read first line from /etc/system-release
        try:
            with open(name='/etc/system-release', mode='rb') as f:
                release = f.readline().strip()
        except Exception as exc:
            raise SystemError('Could not read /etc/system-release. '
                              'Error: {0}'.format(exc))

        # Search the release file for a match against _supported_dists
        matched = match_supported_dist.search(release.lower())
        if matched is None:
            # Release not supported, exit with error
            raise SystemError('Unsupported OS distribution. OS must be one of: '
                              '{0}.'.format(', '.join(supported_dists)))

        # Assign dist,version from the match groups tuple, removing any spaces
        self.dist, self.version = (x.translate(None, ' ') for x in matched.groups())

        # Determine epel_version
        if 'amazon' == self.dist:
            self.epel_version = amazon_epel_versions.get(self.version, None)
        else:
            self.epel_version = self.version.split('.')[0]

        if self.epel_version is None:
            raise SystemError('Unsupported OS version! dist = {0}, version = {1}.'
                              .format(self.dist, self.version))

        logging.debug('Dist\t\t{0}'.format(self.dist))
        logging.debug('Version\t\t{0}'.format(self.version))
        logging.debug('EPEL Version\t{0}'.format(self.epel_version))

    def _repo(self, config):
        """
        Private method that validates that the config is properly formed.
        """
        if not isinstance(config['yumrepomap'], list):
            raise SystemError('`yumrepomap` must be a list!')

    def repo_install(self, configuration):
        """
        Checks the distribution version and installs yum repo definition files
        that are specific to that distribution.

        :param configuration: The configuration data required to install the yum repos.
        :type configuration: JSON
        """

        try:
            config = json.loads(configuration)
        except ValueError:
            logging.fatal('The configuration passed was not properly formed JSON.  Execution Halted.')
            sys.exit(1)

        if 'yumrepomap' in config and config['yumrepomap']:
            self._repo(config)
        else:
            logging.info('yumrepomap did not exist or was empty.')

        self._validate_distro()

        # TODO This block is weird.  Correct and done.
        for repo in config['yumrepomap']:

            if repo['dist'] in [self.dist, 'all']:
                logging.debug('{0} in {1} or all'.format(repo['dist'], self.dist))
                if 'epel_version' in repo and str(repo['epel_version']) != str(self.epel_version):
                    logging.error('epel_version is not valid for this repo. {0}'.format(self.epel_version))
                else:
                    logging.debug('All requirements have been validated for this repo.')
                    # Download the yum repo definition to /etc/yum.repos.d/
                    url = repo['url']
                    repofile = '/etc/yum.repos.d/{0}'.format(url.split('/')[-1])
                    self.download_file(url, repofile)
            else:
                logging.debug('{0} NOT in {1} or all'.format(repo['dist'], self.dist))


class Salt(LinuxManager):
    def __init__(self):
        super(Salt, self).__init__()
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
                logging.error('Detected `git` as the install method, but the required parameter `saltbootstrapsource`',
                              'was not provided.')
            else:
                self.saltbootstrapfilename = self.config['saltbootstrapsource'].split('/')[-1]
            if not self.config['saltgitrepo']:
                logging.error('Detected `git` as the install method, but the required parameter `saltgitrepo` was not ',
                              'provided.')

    def _install_package(self):
        if 'yum' == self.config['saltinstallmethod'].lower():
            self._install_from_yum(self.yum_pkgs)
        elif 'git' == self.config['saltinstallmethod'].lower():
            self.download_file(self.config['saltbootstrapsource'], self.saltbootstrapfilename)
            bootstrapcmd = ['sh', self.saltbootstrapfilename, '-g', self.config['saltgitrepo']]
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
            self.formulaterminationstrings = self.config['formulaterminationstrings']

        self.sourceiss3bucket = self.config['sourceiss3bucket']
        self.entenv = self.config['entenv']
        self.create_working_dir('/usr/tmp/', 'saltinstall')

        self.salt_results_logfile = self.config['salt_results_log'] or os.sep.join((self.workingdir,
                                                                                    'saltcall.results.log'))

        self.salt_debug_logfile = self.config['salt_debug_log'] or os.sep.join((self.workingdir,
                                                                                'saltcall.debug.log'))

        self.saltcall_arguments = ['--out', 'yaml', '--out-file', self.salt_results_logfile, '--return', 'local',
                                   '--log-file', self.salt_debug_logfile, '--log-file-level', 'debug']

        for saltdir in [self.saltfileroot, self.saltbaseenv, self.saltformularoot]:
            try:
                os.makedirs(saltdir)
            except OSError:
                if not os.path.isdir(saltdir):
                    raise

    def _build_salt_formula(self):
        if self.config['saltcontentsource']:
            self.saltcontentfilename = self.config['saltcontentsource'].split('/')[-1]
            self.saltcontentfile = os.sep.join((self.workingdir, self.saltcontentfilename))
            self.download_file(self.config['saltcontentsource'], self.saltcontentfile, self.sourceiss3bucket)
            self.extract_contents(filepath=self.saltcontentfile, to_directory=self.saltsrv)

        # Download and extract any salt formulas specified in formulastoinclude
        formulas_conf = []
        for source_loc in self.formulastoinclude:
            filename = source_loc.split('/')[-1]
            file_loc = os.sep.join((self.workingdir, filename))
            self.download_file(source_loc, file_loc)
            self.extract_contents(filepath=file_loc, to_directory=self.saltformularoot)
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

        self.salt_conf = {'file_roots':
                              {'base': file_roots},
                          'pillar_roots':
                              {'base': [str(self.saltpillarroot)]}
                          }

        with open(os.path.join(self.salt_confpath, 'minion.d', 'watchmaker.conf'), 'w') as f:
            yaml.dump(self.salt_conf, f, default_flow_style=False)

    def install(self, configuration):
        """

        :param configuration:
        :return:
        """

        try:
            self.config = json.loads(configuration)
        except ValueError:
            exceptionhandler('The configuration passed was not properly formed JSON.  Execution Halted.')

        self._configuration_validation()
        self._prepare_for_install()
        self._install_package()
        self._build_salt_formula()

        logging.info('Setting grain `systemprep`...')
        ent_env = {'enterprise_environment': str(self.entenv)}
        cmd = [self.saltcall, '--local', '--retcode-passthrough', 'grains.setval', 'systemprep',
               str(json.dumps(ent_env))]
        self.call_process(cmd)

        if self.config['oupath']:
            print('Setting grain `join-domain`...')
            oupath = {'oupath': self.config['oupath']}
            cmd = [self.saltcall, '--local', '--retcode-passthrough', 'grains.setval', '"join-domain"',
                   json.dumps(oupath)]
            self.call_process(cmd)

        print('Syncing custom salt modules...')
        cmd = [self.saltcall, '--local', '--retcode-passthrough', 'saltutil.sync_all']
        self.call_process(cmd)

        if 'none' == self.config['saltstates'].lower():
            print('No States were specified. Will not apply any salt states.')
        else:
            if 'highstate' == self.config['saltstates'].lower():
                logging.info('Detected the States parameter is set to `highstate`. Applying the salt `"highstate`" '
                             'to the system.')
                cmd = [self.saltcall, '--local', '--retcode-passthrough', 'state.highstate']
                cmd.extend(self.saltcall_arguments)
                self.call_process(cmd)

            else:
                logging.info('Detected the States parameter is set to: {0}. Applying the user-defined list of states '
                             'to the system.'.format(self.config['saltstates']))
                cmd = [self.saltcall, '--local', '--retcode-passthrough', 'state.sls', self.config['saltstates']]
                cmd.extend(self.saltcall_arguments)
                self.call_process(cmd)

        logging.info(
            'Salt states all applied successfully! Details are in the log {0}'.format(self.salt_results_logfile))

        if self.workingdir:
            self.cleanup()
