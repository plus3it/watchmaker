import datetime
import logging
import os
import platform
import subprocess

import yaml
from watchmaker.managers import LinuxWorkersManager, WindowsWorkersManager
from watchmaker.exceptions import SystemFatal as exceptionhandler
from watchmaker import static

class Prepare(object):
    """
    This class is the entry point for watchmaker.  It prepares a system for setup and installation.
    """

    def __init__(self, noreboot=False, s3=False, config_path=None, stream=False, log_path=None):
        """
        :param noreboot: Instances are rebooted after installation.  If this value is set to
        True then the instance will not be rebooted.
        :type noreboot: bool
        :param s3: Should an s3 bucket be used for the installation files.
        :type s3: bool
        :param config_path: Path to YAML configuration file.
        :type config_path: basestring
        :param stream: Enables self.logger to a file.
        :type stream: bool
        :param log_path: Path to logfile for stream self.logger.
        :type log_path: basestring
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
            logging.basicConfig(filename=os.path.join(self.log_path,
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

        :return self.config: Sets the config attribute with the data from the configuration YAML file after validation.
        """

        if self.config_path and not os.path.exists(self.config_path):
            self.logger.warning('User supplied config {0} does not exist.  '
                                'Using the default config.'.format(self.config_path))
            self.config_path = self.default_config
        elif not self.config_path:
            self.logger.warning('User did not supply a config.  Using the default config.')
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

        :return self.system_params: Sets the system_params attribute for a linux system.
        """

        params = {}
        params['prepdir'] = os.path.join('{0}'.format(self.system_drive), 'usr', 'tmp', 'systemprep')
        params['readyfile'] = os.path.join('{0}'.format(self.system_drive), 'var', 'run', 'system-is-ready')
        params['logdir'] = os.path.join('{0}'.format(self.system_drive), 'var', 'log')
        params['workingdir'] = os.path.join('{0}'.format(params['prepdir']), 'workingfiles')
        params['restart'] = 'shutdown -r +1 &'
        self.system_params = params

    def _windows_paths(self):
        """
        Private method for setting up a Windows environment for installation.

        :return self.system_params: Sets the system_params attribute for a Windows system.
        """

        params = {}
        params['prepdir'] = os.path.join('{0}'.format(self.system_drive), 'watchmaker')
        params['readyfile'] = os.path.join('{0}'.format(params['prepdir']), 'system-is-ready')
        params['logdir'] = os.path.join('{0}'.format(params['prepdir']), 'Logs')
        params['workingdir'] = os.path.join('{0}'.format(params['prepdir']), 'WorkingFiles')
        params['shutdown_path'] = os.path.join('{0}'.format(os.environ['SYSTEMROOT']), 'system32', 'shutdown.exe')
        params['restart'] = params["shutdown_path"] + " /r /t 30 /d p:2:4 /c " + \
                            "\"watchmaker complete. Rebooting computer.\""
        self.system_params = params

    def _get_system_params(self):
        """
        Private method for handling the setup of the workspace and environment for the appropriate operating system.
        This method also creates the appropriate directories necessary for installation.

        """

        if 'Linux' in self.system:
            self.system_drive = '/'
            self._linux_paths()
        elif 'Windows' in self.system:
            self.system_drive = os.environ['SYSTEMDRIVE']
            self._windows_paths()
        else:
            self.logger.fatal('System, {0}, is not recognized?'.format(self.system))
            exceptionhandler('The scripts do not recognize this system type: {0}'.format(self.system))

        # Create watchmaker directories
        try:
            if not os.path.exists(self.system_params['logdir']):
                os.makedirs(self.system_params['logdir'])
            if not os.path.exists(self.system_params['workingdir']):
                os.makedirs(self.system_params['workingdir'])
        except Exception as exc:
            self.logger.fatal('Could not create a directory in {0}.\n'
                              'Exception: {1}'.format(self.system_params['prepdir'], exc))
            exceptionhandler(exc)

    def _get_scripts_to_execute(self):
        """
        Private method for parsing configuration data and updating configuration with specified parameters from
        user configuration.

        :return self.execution_scripts: Sets attribute with prepared configuration data for the target system.
        """

        self._get_config_data()

        scriptstoexecute = self.config[self.system]
        for item in self.config[self.system]:
            try:
                self.config[self.system][item]['Parameters'].update(self.kwargs)
            except Exception as exc:
                self.logger.fatal('For {0} in {1} the parameters could not be merged'.format(
                    item,
                    self.config_path
                ))
                exceptionhandler(exc)

        self.execution_scripts = scriptstoexecute

    def install_system(self):
        """
        Method for initiating the installation of the prepared system.  After execution the system should be properly
        provisioned.
        """

        self.logger.info('+' * 80)

        self._get_system_params()
        self.logger.info(self.system_params)

        self._get_scripts_to_execute()
        self.logger.info('Got scripts to execute.')

        if 'Linux' in self.system:
            workers_manager = LinuxWorkersManager(self.s3, self.system_params, self.execution_scripts)
        elif 'Windows' in self.system:
            workers_manager = WindowsWorkersManager(self.s3, self.system_params, self.execution_scripts)
        else:
            exceptionhandler('There is no known System!')

        try:
            workers_manager.worker_cadence()
        except Exception as e:
            exceptionhandler('Execution of the workers cadence has failed. {0}'.format(e))

        if self.noreboot:
            self.logger.info('Detected `noreboot` switch. System will not be rebooted.')
        else:
            self.logger.info('Reboot scheduled. System will reboot after the script exits.')
            subprocess.call(self.system_params['restart'], shell=True)

        self.logger.info('-' * 80)
