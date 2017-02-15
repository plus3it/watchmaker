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


class Arguments(dict):
    """
    Create an arguments object for the :class:`Client`.

    Args:
        config_path (:obj:`str`):
            (Defaults to ``None``) Path or URL to the Watchmaker configuration
            file. If ``None``, the default config.yaml file is used.
        log_dir (:obj:`str`):
            (Defaults to ``None``) See :func:`logger.prepare_logging`.
        noreboot (:obj:`bool`):
            (Defaults to ``False``): Switch to control whether to reboot the
            system upon a successfull execution of
            :func:`WatchmakerClient.install`. When this parameter is set,
            Watchmaker will suppress the reboot. Watchmaker automatically
            suppresses the reboot if it encounters an error.
        verbosity (:obj:`int`):
            (Defaults to ``0``) See :func:`prepare_logging`.

    .. important::

        For all **Keyword Arguments**, below, the default value of ``None``
        means Watchmaker will get the value from the configuration file. Be
        aware that ``None`` and ``'None'`` are two different values, with
        different meanings and effects.

    Keyword Args:

        admingroups (:obj:`str`):
            (Defaults to ``None``) Set a salt grain that specifies the domain
            _groups_ that should have root privileges on Linux or admin
            privileges on Windows. Value must be a colon-separated string. On
            Linux, use the ``^`` to denote spaces in the group name.

            .. code-block:: python

                admingroups = "group1:group2"

                # (Linux only) If there are spaces in the group name, replace
                # the spaces with a '^':
                admingroups = "space^out"

                # (Windows only) If there are spaces in the group name, no
                # special syntax required.
                admingroups = "space out"

        adminusers (:obj:`str`):
            (Defaults to ``None``) Set a salt grain that specifies the domain
            _users_ that should have root privileges on Linux or admin
            privileges on Windows. Value must be a colon-separated string.

            .. code-block:: python

                adminusers = "user1:user2"

        computername (:obj:`str`):
            (Defaults to ``None``) Set a salt grain that specifies the
            computername to apply to the system.
        entenv (:obj:`str`):
            (Defaults to ``None``) Set a salt grain that specifies the
            environment in which the system is being built. For example:
            ``dev``, ``test``, or ``prod``.
        saltstates (:obj:`str`):
            (Defaults to ``None``) Comma-separated string of salt states to
            apply. A value of ``'None'`` (the string) will not apply any salt
            states. A value of ``'Highstate'`` will apply the salt highstate.
        sourceiss3bucket (:obj:`bool`):
            (Defaults to ``None``) Use S3 utilities to retrieve content instead
            of http/s utilities. For S3 utilities to work, the system must have
            boto credentials configured that allow access to the S3 bucket.
        oupath (:obj:`str`):
            (Defaults to ``None``) Set a salt grain that specifies the full DN
            of the OU where the computer account will be created when joining a
            domain.

            .. code-block:: python

                oupath="OU=Super Cool App,DC=example,DC=com"

        extra_arguments (:obj:`list`):
            (Defaults to ``[]``) A list of extra arguments to be merged into
            the worker configurations. The list must be formed as pairs of
            named arguments and values. Any leading hypens in the argument name
            are stripped. For example:

            .. code-block:: python

                extra_arguments=['--arg1', 'value1', '--arg2', 'value2']

                # This list would be converted to the following dict and merged
                # into the parameters passed to the worker configurations:
                {'arg1': 'value1', 'arg2': 'value2'}
    """

    def __init__(  # noqa: D102
        self,
        config_path=None,
        log_dir=None,
        noreboot=False,
        verbosity=0,
        **kwargs
    ):
        self.config_path = config_path
        self.log_dir = log_dir
        self.noreboot = noreboot
        self.verbosity = verbosity
        self.admingroups = kwargs.pop('admingroups', None)
        self.adminusers = kwargs.pop('adminusers', None)
        self.computername = kwargs.pop('computername', None)
        self.entenv = kwargs.pop('entenv', None)
        self.saltstates = kwargs.pop('saltstates', None)
        self.sourceiss3bucket = kwargs.pop('sourceiss3bucket', None)
        self.oupath = kwargs.pop('oupath', None)
        self.extra_arguments = kwargs.pop('extra_arguments', [])

    def __getattr__(self, attr):
        """Support attr-notation for getting dict contents."""
        return super(Arguments, self).__getitem__(attr)

    def __setattr__(self, attr, value):
        """Support attr-notation for setting dict contents."""
        super(Arguments, self).__setitem__(attr, value)


class Client(object):
    """
    Prepare a system for setup and installation.

    Keyword Arguments:
        arguments (:obj:`Arguments`):
            A dictionary of arguments. See :class:`Arguments`.
    """

    def __init__(self, arguments):  # noqa: D102
        self.log = logging.getLogger(
            '{0}.{1}'.format(__name__, self.__class__.__name__)
        )
        self.system = platform.system()
        self._set_system_params()

        # Pop extra_arguments now so we can log it separately
        extra_arguments = arguments.pop('extra_arguments', [])

        header = ' WATCHMAKER RUN '
        header = header.rjust((40 + len(header) // 2), '#').ljust(80, '#')
        self.log.info(header)
        self.log.debug('Parameters:  {0}'.format(arguments))
        self.log.debug('Extra Parameters:  {0}'.format(extra_arguments))
        self.log.debug('System Type: {0}'.format(self.system))
        self.log.debug('System Parameters: {0}'.format(self.system_params))

        # Pop remaining arguments used by watchmaker.Client itself
        self.default_config = os.path.join(static.__path__[0], 'config.yaml')
        self.noreboot = arguments.pop('noreboot', False)
        self.config_path = arguments.pop('config_path')
        self.log_dir = arguments.pop('log_dir')
        self.verbosity = arguments.pop('verbosity')

        # All remaining arguments are worker_args
        worker_args = arguments

        # Convert extra_arguments to a dict and merge it with worker_args
        worker_args.update(dict(
            (k.lstrip('-'), v) for k, v in zip(*[iter(extra_arguments)]*2)
        ))
        # Set self.worker_args, removing `None` values from worker_args
        self.worker_args = dict(
            (k, v) for k, v in worker_args.iteritems() if v is not None
        )

        self.config = self._get_config()

    def _validate_url(self, url):
        return urllib.parse.urlparse(url).scheme in ['http', 'https']

    def _get_config(self):
        """
        Read and validate configuration data for installation.

        Returns:
            dict: Returns the data from the YAML configuration file, scoped to
            the value of ``self.system`` and merged with the value of the
            ``"All"`` key.
        """
        config = {}
        data = ''

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

        config_full = yaml.safe_load(data)
        try:
            config_system = config_full.get(self.system, {})
            config = config_full.get('All', {})
        except AttributeError:
            msg = 'Malformed config file. Must be a dictionary.'
            self.log.critical(msg)
            raise

        # If both config and config_system are empty, raise
        if not config and not config_system:
            msg = 'Malformed config file. No valid workers.'
            self.log.critical(msg)
            raise WatchmakerException(msg)

        # Get the union of workers from config and config_system
        # Merge config_system into config, as needed
        # Merge worker_args (from the cli) into worker configs
        workers = set(config) | set(config_system)
        for worker in workers:
            try:
                if worker in config and worker in config_system:
                    # Worker is present in both, merge the params
                    config[worker]['Parameters'].update(
                        config_system[worker]['Parameters']
                    )
                elif worker in config_system:
                    # Worker is only in config_system, add it to config
                    config[worker] = config_system[worker]
                else:
                    # Worker is only in config, no action needed
                    pass

                self.log.debug(
                    '{0} config: {1}'.format(worker, config[worker])
                )
                # Merge worker_args into config params
                config[worker]['Parameters'].update(self.worker_args)
            except KeyError:
                msg = (
                    'Malformed worker, missing "Parameters" key; worker = {0}'
                    .format(worker)
                )
                self.log.critical(msg)
                raise

        self.log.debug(
            'Arguments merged into worker configs: {0}'
            .format(self.worker_args)
        )

        return config

    def _set_linux_system_params(self):
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

    def _set_windows_system_params(self):
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

    def _set_system_params(self):
        """Set OS-specific attributes."""
        if 'Linux' in self.system:
            self.system_drive = '/'
            self.workers_manager = LinuxWorkersManager
            self._set_linux_system_params()
        elif 'Windows' in self.system:
            self.system_drive = os.environ['SYSTEMDRIVE']
            self.workers_manager = WindowsWorkersManager
            self._set_windows_system_params()
        else:
            msg = 'System, {0}, is not recognized?'.format(self.system)
            self.log.critical(msg)
            raise WatchmakerException(msg)

    def install(self):
        """
        Initiate the installation of the prepared system.

        Upon successful execution, the system will be properly provisioned,
        according to the defined configuration and workers.
        """
        self.log.info('Start time: {0}'.format(datetime.datetime.now()))
        self.log.info(
            'Workers to execute: {0}.'
            .format(self.config.keys())
        )

        # Create watchmaker directories
        try:
            os.makedirs(self.system_params['workingdir'])
        except OSError:
            if not os.path.exists(self.system_params['workingdir']):
                msg = (
                    'Unable create directory - {0}'
                    .format(self.system_params['workingdir'])
                )
                self.log.critical(msg)
                raise

        workers_manager = self.workers_manager(
            system_params=self.system_params,
            workers=self.config
        )

        try:
            workers_manager.worker_cadence()
        except:
            msg = 'Execution of the workers cadence has failed.'
            self.log.critical(msg)
            raise

        if self.noreboot:
            self.log.info(
                'Detected `noreboot` switch. System will not be rebooted.'
            )
        else:
            self.log.info(
                'Reboot scheduled. System will reboot after the script exits.'
            )
            subprocess.call(self.system_params['restart'], shell=True)
        self.log.info('Stop time: {0}'.format(datetime.datetime.now()))
