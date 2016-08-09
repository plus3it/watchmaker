import datetime
import logging
import os
import platform
import subprocess

import yaml

from watchmaker import static
from watchmaker.exceptions import SystemFatal as exceptionhandler
from watchmaker.managers.workers import (LinuxWorkersManager,
                                         WindowsWorkersManager)

__version__ = '0.0.1'


class Prepare(object):
    """
    Prepare a system for setup and installation.
    """
    def __init__(
            self,
            noreboot=False,
            s3=False,
            config_path=None,
            stream=False,
            log_path=None):
        """
        Args:
            noreboot (bool):
                Instances are rebooted after installation.  If this value is
                set to True then the instance will not be rebooted.
            s3 (bool):
                Should an s3 bucket be used for the installation files.
            config_path (str):
                Path to YAML configuration file.
            stream (bool):
                Enables self.logger to a file.
            log_path (str):
                Path to logfile for stream self.logger.
        """
        self.kwargs = {}
        self.noreboot = noreboot
        self.s3 = s3
        self.system = platform.system()
        self.config_path = config_path
        self.default_config = os.path.join(static.__path__[0], 'config.yaml')
        self.log_path = log_path
        self.config = None
        self.system_params = None
        self.system_drive = None
        self.execution_scripts = None
        self.logger = logging.getLogger()

        if stream and os.path.exists(log_path):
            logging.basicConfig(
                filename=os.path.join(
                    self.log_path,
                    'watchmaker-{0}.log'.format(str(datetime.date.today()))),
                format='%(levelname)s:\t%(message)s',
                level=logging.DEBUG)
            self.logger = logging.getLogger()
            self.logger.info('\n\n\n{0}'.format(datetime.datetime.now()))
        elif stream:
            self.logger.error('{0} does not exist'.format(log_path))
        else:
            self.logger.warning('Stream logger is not enabled!')

        self.logger.info('Parameters:  {0}'.format(self.kwargs))
        self.logger.info('System Type: {0}'.format(self.system))

    def _get_config_data(self):
        """
        Private method for reading configuration data for installation.

        Returns:
            Sets the self.config attribute with the data from the
            configuration YAML file after validation.
        """

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
        self.logger.info('+' * 80)

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
                self.execution_scripts
            )
        elif 'Windows' in self.system:
            workers_manager = WindowsWorkersManager(
                self.s3,
                self.system_params,
                self.execution_scripts
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

        self.logger.info('-' * 80)
