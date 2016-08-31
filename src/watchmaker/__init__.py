import datetime
import logging
import os
import platform
import shutil
import subprocess
import sys
import yaml

from six.moves import urllib
from watchmaker import static
from watchmaker.exceptions import SystemFatal as exceptionhandler
from watchmaker.managers.workers import (LinuxWorkersManager,
                                         WindowsWorkersManager)

__version__ = '0.0.1'


class PrepArguments(object):

    def __init__(self):
        self.noreboot = False
        self.s3 = False
        self.config_path = None
        self.saltstates = False

    def __repr__(self):
        return '< noreboot="{0}", s3="{1}", config_path="{2}"' \
               ', saltstates="{3}" >'.format(self.noreboot,
                                             self.s3,
                                             self.config_path,
                                             self.saltstates
                                             )


class Prepare(object):
    """
    Prepare a system for setup and installation.
    """
    def __init__(self, arguments):
        """
        Args:
            noreboot (bool):
                Instances are rebooted after installation.  If this value is
                set to True then the instance will not be rebooted.
            s3 (bool):
                Should an s3 bucket be used for the installation files.
            config_path (str):
                Path to YAML configuration file.
            logger (bool):
                Enables self.logger to a file.
            log_path (str):
                Path to log directory for stream self.logger.
        """
        self.kwargs = {}
        self.noreboot = arguments.noreboot
        self.s3 = arguments.sourceiss3bucket
        self.system = platform.system()
        self.config_path = arguments.config
        self.default_config = os.path.join(static.__path__[0], 'config.yaml')
        self.saltstates = arguments.saltstates
        self.config = None
        self.system_params = None
        self.system_drive = None
        self.execution_scripts = None

        self._prepare_logger(arguments.log_path)
        self.logger.info('Parameters:  {0}'.format(self.kwargs))
        self.logger.info('System Type: {0}'.format(self.system))
        sys.exit()

    def _prepare_logger(self, log_path):
        if log_path and os.path.exists(log_path):
            logging.basicConfig(
                filename=os.path.join(
                    log_path,
                    'watchmaker-{0}.log'.format(str(datetime.date.today()))),
                format='%(levelname)s:\t%(message)s',
                level=logging.DEBUG)
            self.logger = logging.getLogger()
            self.logger.info(
                'Logging time: {0}'.format(datetime.datetime.now())
            )
        elif not log_path:
            logging.basicConfig()
            self.logger = logging.getLogger()
            self.logger.warning('Stream logger is not enabled!')
        else:
            logging.basicConfig()
            self.logger = logging.getLogger()
            self.logger.error('{0} does not exist'.format(log_path))

    def _validate_url(self, url):

        return urllib.parse.urlparse(url).scheme in ['http', 'https']

    def _get_config_data(self):
        """
        Private method for reading configuration data for installation.

        Returns:
            Sets the self.config attribute with the data from the
            configuration YAML file after validation.
        """

        if self._validate_url(self.config_path):
            try:
                response = urllib.request.urlopen(self.config_path)
                with open('config.yaml', 'wb') as outfile:
                    shutil.copyfileobj(response, outfile)
                self.config_path = 'config.yaml'
            except urllib.error.URLError:
                print('The URL used to get the user config.yaml file did not '
                      'work!\nPlease make sure your config is available.')
                sys.exit(1)

        if self.config_path and not os.path.exists(self.config_path):
            self.logger.warning(
                'User supplied config {0} does not exist. '
                'Using the default config.'.format(self.config_path)
            )
            self.config_path = self.default_config
        elif not self.config_path:
            self.logger.warning(
                'User did not supply a config.  Using the default config.'
            )
            self.config_path = self.default_config
        else:
            self.logger.info('User supplied config being used.')
        with open(self.config_path) as f:
            data = f.read()

        if data:
            self.config = yaml.load(data)
        else:
            logging.debug('No data to load.')

    def _linux_paths(self):
        """
        Private method for setting up a linux environment for installation.

        Returns:
            dict: Map of system_params for a Linux system.
        """

        params = {}
        params['prepdir'] = os.path.join(
            '{0}'.format(self.system_drive), 'usr', 'tmp', 'systemprep')
        params['readyfile'] = os.path.join(
            '{0}'.format(self.system_drive), 'var', 'run', 'system-is-ready')
        params['logdir'] = os.path.join(
            '{0}'.format(self.system_drive), 'var', 'log')
        params['workingdir'] = os.path.join(
            '{0}'.format(params['prepdir']), 'workingfiles')
        params['restart'] = 'shutdown -r +1 &'
        self.system_params = params

    def _windows_paths(self):
        """
        Private method for setting up a Windows environment for installation.

        Returns:
            dict: Map of system_params for a Windows system.
        """
        params = {}
        # os.path.join does not produce path as expected when first string
        # ends in colon; so using a join on the sep character.
        params['prepdir'] = os.path.sep.join([self.system_drive, 'Watchmaker'])
        params['readyfile'] = os.path.join(
            '{0}'.format(params['prepdir']), 'system-is-ready')
        params['logdir'] = os.path.join(
            '{0}'.format(params['prepdir']), 'Logs')
        params['workingdir'] = os.path.join(
            '{0}'.format(params['prepdir']), 'WorkingFiles')
        params['shutdown_path'] = os.path.join(
            '{0}'.format(os.environ['SYSTEMROOT']), 'system32', 'shutdown.exe')
        params['restart'] = params["shutdown_path"] + \
            ' /r /t 30 /d p:2:4 /c ' + \
            '"Watchmaker complete. Rebooting computer."'
        self.system_params = params

    def _get_system_params(self):
        """
        Handles the setup of the OS workspace and environment.

        This method also creates the appropriate directories necessary for
        installation.
        """
        if 'Linux' in self.system:
            self.system_drive = '/'
            self._linux_paths()
        elif 'Windows' in self.system:
            self.system_drive = os.environ['SYSTEMDRIVE']
            self._windows_paths()
        else:
            self.logger.fatal('System, {0}, is not recognized?'
                              .format(self.system))
            exceptionhandler('The scripts do not recognize this system type: '
                             '{0}'.format(self.system))

        # Create watchmaker directories
        try:
            if not os.path.exists(self.system_params['logdir']):
                os.makedirs(self.system_params['logdir'])
            if not os.path.exists(self.system_params['workingdir']):
                os.makedirs(self.system_params['workingdir'])
        except Exception as exc:
            self.logger.fatal('Could not create a directory in {0}.\n'
                              'Exception: {1}'
                              .format(self.system_params['prepdir'], exc))
            exceptionhandler(exc)

    def _get_scripts_to_execute(self):
        """
        Parses and updates configuration data.

        Returns:
            list: Attribute with configuration data for the target system.
        """
        self._get_config_data()

        scriptstoexecute = self.config[self.system]
        for item in self.config[self.system]:
            try:
                self.config[self.system][item]['Parameters'].update(
                    self.kwargs)
            except Exception as exc:
                self.logger.fatal(
                    'For {0} in {1} the parameters could not be merged'
                    .format(item, self.config_path)
                )
                exceptionhandler(exc)

        self.execution_scripts = scriptstoexecute

    def install_system(self):
        """
        Initiate the installation of the prepared system.

        After execution the system should be properly provisioned.
        """
        self._get_system_params()
        self.logger.info(self.system_params)

        self._get_scripts_to_execute()
        self.logger.info(
            'Got scripts to execute: {0}.'
            .format(self.config[self.system].keys())
        )

        if 'Linux' in self.system:
            workers_manager = LinuxWorkersManager(
                self.s3,
                self.system_params,
                self.execution_scripts,
                self.saltstates
            )
        elif 'Windows' in self.system:
            workers_manager = WindowsWorkersManager(
                self.s3,
                self.system_params,
                self.execution_scripts,
                self.saltstates
            )
        else:
            exceptionhandler('There is no known System!')

        try:
            workers_manager.worker_cadence()
        except Exception as e:
            exceptionhandler('Execution of the workers cadence has failed. {0}'
                             .format(e))

        if self.noreboot:
            self.logger.info('Detected `noreboot` switch. System will not be '
                             'rebooted.')
        else:
            self.logger.info('Reboot scheduled. System will reboot after the '
                             'script exits.')
            subprocess.call(self.system_params['restart'], shell=True)
