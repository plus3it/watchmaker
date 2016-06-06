import os
import re
import sys
import json
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
        self.verstion = None
        self.epel_version = None

    def _validate_distro(self):
        """
        Private method for validating the linux distrbution uses yum and is configurable.
        """

        self.dist = None
        self.verstion = None
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
        release = None
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

        scriptname = __file__
        logging.info('+' * 80)
        logging.info('Entering script -- {0}'.format(scriptname))
        logging.info('Printing parameters...')

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

        logging.info('{0} complete!'.format(scriptname))
        logging.info('-' * 80)


class Salt(LinuxManager):

    def __init__(self):
        super(Salt, self).__init__()
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

    def _prepare_for_install(self):

        if self.config['formulastoinclude']:
            self.formulastoinclude = self.config['formulastoinclude']

        if self.config['formulaterminationstrings']:
            self.formulaterminationstrings = self.config['formulaterminationstrings']

        self.sourceiss3bucket =  self.config['sourceiss3bucket']

        self.entenv = self.config['entenv']

        self.create_working_dir('/usr/tmp/', 'saltinstall')

        self.salt_results_logfile = self.config['salt_results_log'] or os.sep.join((self.workingdir,
                                                                                    'saltcall.results.log'))

        self.salt_debug_logfile = self.config['salt_debug_log'] or os.sep.join((self.workingdir,
                                                                                'saltcall.debug.log'))


        self.saltcall_arguments = ['--out', 'yaml', '--out-file', self.salt_results_logfile, '--return local',
                                   '--log-file', self.salt_debug_logfile, '--log-file-level', 'debug']

        for saltdir in [self.saltfileroot, self.saltbaseenv, self.saltformularoot]:
            try:
                os.makedirs(saltdir)
            except OSError:
                if not os.path.isdir(saltdir):
                    raise

    def _install_package(self):
        if 'yum' == self.config['saltinstallmethod'].lower():
            self._install_from_yum(self.yum_pkgs)

        elif 'git' == self.config['saltinstallmethod'].lower():

            self.download_file(self.config['saltbootstrapsource'], self.saltbootstrapfile)

            bootstrapcmd = ['sh', self.saltbootstrapfile, '-g', self.config['saltgitrepo']]

            if self.config['saltversion']:
                bootstrapcmd.append('git')
                bootstrapcmd.append(self.config['saltversion'])
            else:
                logging.debug('No salt version defined in config.')

            subprocess.call([bootstrapcmd])


def install(self, configuration):
        """

        :param configuration:
        :return:
        """

        try:
            self.config = json.loads(configuration)
        except ValueError:
            exceptionhandler('The configuration passed was not properly formed JSON.  Execution Halted.')

        try:
            self._configuration_validation()
        except:
            exceptionhandler('Configuration for Salt did not validate.')

        try:
            self._prepare_for_install()
        except:
            exceptionhandler('Preparation for Salt install failed.')

        try:
            self._install_package()
        except:
            exceptionhandler('Installation of Salt package failed.')


        if self.config['saltcontentsource']:
            self.saltcontentfilename = self.config['saltcontentsource'].split('/')[-1]
            self.saltcontentfile = os.sep.join((self.workingdir, self.saltcontentfilename))
            self.download_file(self.config['saltcontentsource'], self.saltcontentfile, self.sourceiss3bucket)
            self.extract_contents(filepath=self.saltcontentfile,
                             to_directory=self.saltsrv)

        #Download and extract any salt formulas specified in formulastoinclude
        saltformulaconf = []
        for formulasource in formulastoinclude:
            formulafilename = formulasource.split('/')[-1]
            formulafile = os.sep.join((self.workingdir, formulafilename))
            self.download_file(formulasource, formulafile)
            self.extract_contents(filepath=formulafile,
                             to_directory=saltformularoot)
            formulafilebase = '.'.join(formulafilename.split('.')[:-1])
            formuladir = os.sep.join((saltformularoot, formulafilebase))
            for string in formulaterminationstrings:
                if formulafilebase.endswith(string):
                    newformuladir = formuladir[:-len(string)]
                    if os.path.exists(newformuladir):
                        shutil.rmtree(newformuladir)
                    shutil.move(formuladir, newformuladir)
                    formuladir = newformuladir
            saltformulaconf += '    - {0}\n'.format(formuladir),

        #Create a list that contains the new file_roots configuration
        saltfilerootconf = []
        saltfilerootconf += 'file_roots:\n',
        saltfilerootconf += '  base:\n',
        saltfilerootconf += '    - {0}\n'.format(saltbaseenv),
        saltfilerootconf += saltformulaconf
        saltfilerootconf += '\n',

        #Create a list that contains the new pillar_roots configuration
        saltpillarrootconf = []
        saltpillarrootconf += 'pillar_roots:\n',
        saltpillarrootconf += '  base:\n',
        saltpillarrootconf += '    - {0}\n\n'.format(saltpillarroot),

        #Backup the minionconf file
        shutil.copyfile(minionconf, '{0}.bak'.format(minionconf))

        #Read the minionconf file into a list
        with open(minionconf, 'r') as f:
            minionconflines = f.readlines()

        #Find the file_roots section in the minion conf file
        filerootsbegin = '^#file_roots:|^file_roots:'
        filerootsend = '#$|^$'
        beginindex = None
        endindex = None
        n = 0
        for line in minionconflines:
            if re.match(filerootsbegin, line):
                beginindex = n
            if beginindex and not endindex and re.match(filerootsend, line):
                endindex = n
            n += 1

        #Update the file_roots section with the new configuration
        minionconflines = minionconflines[0:beginindex] + \
                          saltfilerootconf + minionconflines[endindex + 1:]

        #Find the pillar_roots section in the minion conf file
        pillarrootsbegin = '^#pillar_roots:|^pillar_roots:'
        pillarrootsend = '^#$|^$'
        beginindex = None
        endindex = None
        n = 0
        for line in minionconflines:
            if re.match(pillarrootsbegin, line):
                beginindex = n
            if beginindex and not endindex and re.match(pillarrootsend, line):
                endindex = n
            n += 1

        #Update the pillar_roots section with the new configuration
        minionconflines = minionconflines[0:beginindex] + \
                          saltpillarrootconf + minionconflines[endindex + 1:]

        #Write the new configuration to minionconf
        try:
            with open(minionconf, 'w') as f:
                f.writelines(minionconflines)
        except Exception as exc:
            raise SystemError('Could not write to minion conf file: {0}\n'
                              'Exception: {1}'.format(minionconf, exc))
        else:
            print('Saved the new minion configuration successfully.')

        # Write custom grains
        if entenv == True:
            # TODO: Get environment from EC2 metadata or tags
            entenv = entenv
        print('Setting grain `systemprep`...')
        systemprepgrainresult = os.system(
            '{0} --local grains.setval systemprep \'{{"enterprise_environment":'
            '"{1}"}}\''.format(saltcall, entenv))
        if config['oupath']:
            print('Setting grain `join-domain`...')
            joindomaingrainresult = os.system(
                '{0} --local grains.setval "join-domain" \'{{"oupath":'
                '"{1}"}}\''.format(saltcall, config['oupath']))

        # Sync custom modules
        print('Syncing custom salt modules...')
        systemprepsyncresult = os.system(
            '{0} --local saltutil.sync_all'.format(saltcall))

        # Check whether we need to run salt-call
        if 'none' == config['saltstates'].lower():
            print('No States were specified. Will not apply any salt states.')
        else:
            # Apply the requested salt state(s)
            result = None
            if 'highstate' == config['saltstates'].lower():
                print('Detected the States parameter is set to `highstate`. '
                      'Applying the salt `"highstate`" to the system.')
                result = os.system('{0} --local state.highstate {1}'
                            .format(saltcall, saltcall_arguments))
            else:
                print('Detected the States parameter is set to: {0}. '
                      'Applying the user-defined list of states to the system.'
                      .format(config['saltstates']))
                result = os.system('{0} --local state.sls {1} {2}'
                            .format(saltcall, config['saltstates'], saltcall_arguments))

            print('Return code of salt-call: {0}'.format(result))

            # Check for errors in the salt state execution
            try:
                with open(salt_results_logfile, 'rb') as f:
                    salt_results = f.read()
            except Exception as exc:
                error_message = 'Could open the salt results log file: {0}\n' \
                                'Exception: {1}' \
                                .format(salt_results_logfile, exc)
                raise SystemError(error_message)
            if (not re.search('result: false', salt_results)) and \
               (re.search('result: true', salt_results)):
                #At least one state succeeded, and no states failed, so log success
                print('Salt states applied successfully! Details are in the log, '
                      '{0}'.format(salt_results_logfile))
            else:
                error_message = 'ERROR: There was a problem running the salt ' \
                                'states! Check for errors and failed states in ' \
                                'the log file: {0}' \
                                .format(salt_results_logfile)
                raise SystemError(error_message)

        #Remove working files
        if self.workingdir:
            self.cleanup()

        print('Salt Install complete!')
        print('-' * 80)
