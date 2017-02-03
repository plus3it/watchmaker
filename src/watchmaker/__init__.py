# -*- coding: utf-8 -*-
"""Watchmaker module."""
import datetime
import logging
import os
import platform
import subprocess

import yaml

from six.moves import urllib

from watchmaker import static
from watchmaker.exceptions import WatchmakerException
from watchmaker.managers.workers import (LinuxWorkersManager,
                                         WindowsWorkersManager)

__version__ = '0.0.1'


class PrepArguments(object):
    """Prepare arguments."""

    def __init__(self):  # noqa: D102
        self.noreboot = False
        self.s3 = False
        self.config_path = None
        self.saltstates = False

    def __repr__(self):  # noqa: D105
        return '< noreboot="{0}", s3="{1}", config_path="{2}"' \
               ', saltstates="{3}" >'.format(self.noreboot,
                                             self.s3,
                                             self.config_path,
                                             self.saltstates
                                             )


class Prepare(object):
    """
    Prepare a system for setup and installation.

    Args:
        arguments (:obj:`dict`):
            A dictionary of arguments. See :func:`cli.main`.
    """

    def __init__(self, arguments):  # noqa: D102
        self.log = logging.getLogger(
            '{0}.{1}'.format(__name__, self.__class__.__name__)
        )
        self.worker_args = {
            'sourceiss3bucket': arguments.sourceiss3bucket,
            'saltstates': arguments.saltstates,
            'admingroups': arguments.admingroups,
            'adminusers': arguments.adminusers,
            'computername': arguments.computername,
            'entenv': arguments.entenv,
            'oupath': arguments.oupath,
        }
        self.noreboot = arguments.noreboot
        self.system = platform.system()
        self.config_path = arguments.config
        self.default_config = os.path.join(static.__path__[0], 'config.yaml')
        self.config = self._get_config_data()
        self.system_params = None
        self.system_drive = None
        self.execution_scripts = None

        header = ' WATCHMAKER RUN '
        header = header.rjust((40 + len(header) // 2), '#').ljust(80, '#')
        self.log.info(header)
        self.log.info('Parameters:  {0}'.format(arguments))
        self.log.info('System Type: {0}'.format(self.system))

    def _validate_url(self, url):
        return urllib.parse.urlparse(url).scheme in ['http', 'https']

    def _get_config_data(self):
        """
        Read and validate configuration data for installation.

        Returns:
            dict: Data from the YAML configuration file.
        """
        data = {}

        if not self.config_path:
            self.log.warning(
                'User did not supply a config.  Using the default config.'
            )
            self.config_path = self.default_config
        else:
            self.log.info('User supplied config being used.')

        if self._validate_url(self.config_path):
            try:
                data = urllib.request.urlopen(self.config_path).read()
            except urllib.error.URLError:
                msg = (
                    'The URL used to get the user config.yaml file did not '
                    'work!  Please make sure your config is available.'
                )
                self.log.critical(msg)
                raise
        elif self.config_path and not os.path.exists(self.config_path):
            msg = (
                'User supplied config {0} does not exist.  Please '
                'double-check your config path or use the default config '
                'path.'.format(self.config_path)
            )
            self.log.critical(msg)
            raise WatchmakerException(msg)
        else:
            with open(self.config_path) as f:
                data = f.read()

        if data:
            return(yaml.safe_load(data))
        else:
            msg = 'Encountered an unknown error loading the config. Aborting!'
            self.log.critical(msg)
            raise WatchmakerException(msg)

    def _linux_paths(self):
        """Set ``self.system_params`` attribute for Linux systems."""
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
        """Set ``self.system_params`` attribute for Windows systems."""
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
        """Set OS-specific attributes."""
        if 'Linux' in self.system:
            self.system_drive = '/'
            self._linux_paths()
        elif 'Windows' in self.system:
            self.system_drive = os.environ['SYSTEMDRIVE']
            self._windows_paths()
        else:
            msg = 'System, {0}, is not recognized?'.format(self.system)
            self.log.critical(msg)
            raise WatchmakerException(msg)

        # Create watchmaker directories
        try:
            if not os.path.exists(self.system_params['logdir']):
                os.makedirs(self.system_params['logdir'])
            if not os.path.exists(self.system_params['workingdir']):
                os.makedirs(self.system_params['workingdir'])
        except Exception:
            msg = (
                'Could not create a directory in {0}.'
                .format(self.system_params['prepdir'])
            )
            self.log.critical(msg)
            raise

    def _get_scripts_to_execute(self):
        """Set ``self.execution_scripts`` attribute with configuration data."""
        scriptstoexecute = self.config[self.system]

        # Remove `None` values from worker_args
        worker_args = dict(
            (k, v) for k, v in self.worker_args.iteritems() if v is not None
        )
        self.log.debug(
            'Arguments being merged into worker configs: {0}'
            .format(worker_args)
        )

        for item in self.config[self.system]:
            try:
                self.config[self.system][item]['Parameters'].update(
                    worker_args
                )
            except Exception:
                msg = (
                    'For {0} in {1}, the parameters could not be merged.'
                    .format(item, self.config_path)
                )
                self.log.critical(msg)
                raise

        self.execution_scripts = scriptstoexecute

    def install_system(self):
        """
        Initiate the installation of the prepared system.

        Upon successful execution, the system will be properly provisioned,
        according to the defined configuration and workers.
        """
        self._get_system_params()
        self.log.debug(self.system_params)

        self._get_scripts_to_execute()
        self.log.info(
            'Got scripts to execute: {0}.'
            .format(self.config[self.system].keys())
        )

        if 'Linux' in self.system:
            workers_manager = LinuxWorkersManager(
                self.system_params,
                self.execution_scripts
            )
        elif 'Windows' in self.system:
            workers_manager = WindowsWorkersManager(
                self.system_params,
                self.execution_scripts
            )
        else:
            msg = 'There is no known System!'
            self.log.critical(msg)
            raise WatchmakerException(msg)

        try:
            workers_manager.worker_cadence()
        except Exception:
            msg = 'Execution of the workers cadence has failed.'
            self.log.critical(msg)
            raise

        self.log.info('Stop time: {0}'.format(datetime.datetime.now()))
        if self.noreboot:
            self.log.info(
                'Detected `noreboot` switch. System will not be rebooted.'
            )
        else:
            self.log.info(
                'Reboot scheduled. System will reboot after the script exits.'
            )
            subprocess.call(self.system_params['restart'], shell=True)
