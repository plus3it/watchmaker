# -*- coding: utf-8 -*-
"""Watchmaker module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import datetime
import logging
import os
import platform
import re
import subprocess

import importlib_metadata
import oschmod
import yaml

import watchmaker.utils
from watchmaker.config import get_configs
from watchmaker.exceptions import InvalidValueError, WatchmakerError
from watchmaker.logger import log_system_details
from watchmaker.managers.worker_manager import (
    LinuxWorkersManager,
    WindowsWorkersManager,
)
from watchmaker.status import Status


def _extract_version(package_name):
    return importlib_metadata.version(package_name)


def _version_info(app_name, version):
    return "{0}/{1} Python/{2} {3}/{4}".format(
        app_name,
        version,
        platform.python_version(),
        platform.system(),
        platform.release(),
    )


__version__ = _extract_version("watchmaker")
VERSION_INFO = _version_info("Watchmaker", __version__)


class Arguments(dict):
    """
    Create an arguments object for the :class:`watchmaker.Client`.

    Args:
        config_path: (:obj:`str`)
            Path or URL to the Watchmaker configuration
            file. If ``None``, the default config.yaml file is used.
            (*Default*: ``None``)

        log_dir: (:obj:`str`)
            Path to a directory. If set, Watchmaker logs to a file named
            ``watchmaker.log`` in the specified directory. Both the directory
            and the file will be created if necessary. If the file already
            exists, Watchmaker appends to it rather than overwriting it. If
            this argument evaluates to ``False``, then logging to a file is
            disabled. Watchmaker will always output to stdout/stderr.
            Additionaly, Watchmaker workers may use this directory to keep
            other log files.
            (*Default*: ``None``)

        no_reboot: (:obj:`bool`)
            Switch to control whether to reboot the system upon a successful
            execution of :func:`watchmaker.Client.install`. When this parameter
            is set, Watchmaker will suppress the reboot. Watchmaker
            automatically suppresses the reboot if it encounters an error.
            (*Default*: ``False``)

        log_level: (:obj:`str`)
            Level to log at. Case-insensitive. Valid options include,
            from least to most verbose:

            - ``critical``
            - ``error``
            - ``warning``
            - ``info``
            - ``debug``

    .. important::

        For all **Keyword Arguments**, below, the default value of ``None``
        means Watchmaker will get the value from the configuration file. Be
        aware that ``None`` and ``'None'`` are two different values, with
        different meanings and effects.

    Keyword Arguments:
        admin_groups: (:obj:`str`)
            Set a salt grain that specifies the domain
            _groups_ that should have root privileges on Linux or admin
            privileges on Windows. Value must be a colon-separated string. On
            Linux, use the ``^`` to denote spaces in the group name.
            (*Default*: ``None``)

            .. code-block:: python

                admin_groups = "group1:group2"

                # (Linux only) The group names must be lowercased. Also, if
                # there are spaces in a group name, replace the spaces with a
                # '^'.
                admin_groups = "space^out"

                # (Windows only) No special capitalization nor syntax
                # requirements.
                admin_groups = "Space Out"

        admin_users: (:obj:`str`)
            Set a salt grain that specifies the domain
            _users_ that should have root privileges on Linux or admin
            privileges on Windows. Value must be a colon-separated string.
            (*Default*: ``None``)

            .. code-block:: python

                admin_users = "user1:user2"

        computer_name: (:obj:`str`)
            Set a salt grain that specifies the computername to apply to the
            system.
            (*Default*: ``None``)

        environment: (:obj:`str`)
            Set a salt grain that specifies the environment in which the system
            is being built. For example: ``dev``, ``test``, or ``prod``.
            (*Default*: ``None``)

        salt_states: (:obj:`str`)
            Comma-separated string of salt states to apply. A value of
            ``None`` will not apply any salt states. A value of ``'Highstate'``
            will apply the salt highstate.
            (*Default*: ``None``)

        ou_path: (:obj:`str`)
            Set a salt grain that specifies the full DN of the OU where the
            computer account will be created when joining a domain.
            (*Default*: ``None``)

            .. code-block:: python

                ou_path="OU=Super Cool App,DC=example,DC=com"

        extra_arguments: (:obj:`list`)
            A list of extra arguments to be merged into the worker
            configurations. The list must be formed as pairs of named arguments
            and values. Any leading hypens in the argument name are stripped.
            (*Default*: ``[]``)

            .. code-block:: python

                extra_arguments=['--arg1', 'value1', '--arg2', 'value2']

                # This list would be converted to the following dict and merged
                # into the parameters passed to the worker configurations:
                {'arg1': 'value1', 'arg2': 'value2'}

    """

    DEFAULT_VALUE = "WAM_NONE"

    def __init__(
        self,
        config_path=None,
        log_dir=None,
        no_reboot=False,
        log_level=None,
        *args,
        **kwargs
    ):
        super(Arguments, self).__init__(*args, **kwargs)
        self.config_path = config_path
        self.log_dir = log_dir
        self.no_reboot = no_reboot
        self.log_level = log_level
        self.admin_groups = watchmaker.utils.clean_none(
            kwargs.pop("admin_groups", None) or Arguments.DEFAULT_VALUE
        )
        self.admin_users = watchmaker.utils.clean_none(
            kwargs.pop("admin_users", None) or Arguments.DEFAULT_VALUE
        )
        self.computer_name = watchmaker.utils.clean_none(
            kwargs.pop("computer_name", None) or Arguments.DEFAULT_VALUE
        )
        self.environment = watchmaker.utils.clean_none(
            kwargs.pop("environment", None) or Arguments.DEFAULT_VALUE
        )
        self.salt_states = watchmaker.utils.clean_none(
            kwargs.pop("salt_states", None) or Arguments.DEFAULT_VALUE
        )
        self.ou_path = watchmaker.utils.clean_none(
            kwargs.pop("ou_path", None) or Arguments.DEFAULT_VALUE
        )

        # Parse extra_arguments passed as `--argument=value` into separate
        # tokens, ['--argument', 'value']. This way the `=` as the separator is
        # treated the same as the ` ` as the separator, e.g. `--argument value`
        extra_arguments = []
        for item in kwargs.pop("extra_arguments", None) or []:
            match = re.match("^(?P<arg>-+.*?)=(?P<val>.*)", item)
            if match:
                # item is using '=' to separate argument name and value
                extra_arguments.extend(
                    [
                        match.group("arg"),
                        watchmaker.utils.clean_none(
                            match.group("val") or Arguments.DEFAULT_VALUE
                        ),
                    ]
                )
            elif item.startswith("-"):
                # item is the argument name
                extra_arguments.extend([item])
            else:
                # item is the argument value
                extra_arguments.extend(
                    [
                        watchmaker.utils.clean_none(
                            item or Arguments.DEFAULT_VALUE)
                    ]
                )

        self.extra_arguments = extra_arguments

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
        arguments: (:obj:`Arguments`)
            A dictionary of arguments. See :class:`watchmaker.Arguments`.

    """

    def __init__(self, arguments):
        self.log = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        # Pop extra_arguments now so we can log it separately
        extra_arguments = arguments.pop("extra_arguments", [])

        header = " WATCHMAKER RUN "
        header = header.rjust((40 + len(header) // 2), "#").ljust(80, "#")
        self.log.info(header)
        self.log.debug("Watchmaker Version: %s", __version__)
        self.log.debug("Parameters: %s", arguments)
        self.log.debug("Extra Parameters: %s", extra_arguments)

        # Pop remaining arguments used by watchmaker.Client itself
        self.no_reboot = arguments.pop("no_reboot", False)
        self.config_path = arguments.pop("config_path")
        self.log_dir = arguments.pop("log_dir")
        self.log_level = arguments.pop("log_level")

        log_system_details(self.log)

        # Get the system params
        self.system = platform.system().lower()
        self._set_system_params()

        self.log.debug("System Parameters: %s", self.system_params)

        # All remaining arguments are worker_args
        self.worker_args = self._get_worker_args(arguments, extra_arguments)

        self.config, status_config = \
            get_configs(self.system,
                        self.worker_args,
                        self.config_path)

        self.status = Status(status_config)

        self.status.update_status("RUNNING")

    def _get_linux_system_params(self):
        """Set ``self.system_params`` attribute for Linux systems."""
        params = {}
        params["prepdir"] = os.path.join(
            "{0}".format(self.system_drive), "usr", "tmp", "watchmaker"
        )
        params["readyfile"] = os.path.join(
            "{0}".format(self.system_drive), "var", "run", "system-is-ready"
        )
        params["logdir"] = os.path.join("{0}".format(self.system_drive),
                                        "var", "log")
        params["workingdir"] = os.path.join(
            "{0}".format(params["prepdir"]), "workingfiles"
        )
        params["restart"] = "shutdown -r +1 &"
        return params

    def _get_windows_system_params(self):
        """Set ``self.system_params`` attribute for Windows systems."""
        params = {}
        # os.path.join does not produce path as expected when first string
        # ends in colon; so using a join on the sep character.
        params["prepdir"] = os.path.sep.join([self.system_drive, "Watchmaker"])
        params["readyfile"] = os.path.join(
            "{0}".format(params["prepdir"]), "system-is-ready"
        )
        params["logdir"] = \
            os.path.join("{0}".format(params["prepdir"]), "Logs")
        params["workingdir"] = os.path.join(
            "{0}".format(params["prepdir"]), "WorkingFiles"
        )
        params["shutdown_path"] = os.path.join(
            "{0}".format(os.environ["SYSTEMROOT"]), "system32", "shutdown.exe"
        )
        params["restart"] = (
            params["shutdown_path"]
            + " /r /t 30 /d p:2:4 /c "
            + '"Watchmaker complete. Rebooting computer."'
        )
        return params

    def _set_system_params(self):
        """Set OS-specific attributes."""
        if "linux" in self.system:
            self.system_drive = "/"
            self.workers_manager = LinuxWorkersManager
            self.system_params = self._get_linux_system_params()
            os.umask(0o077)
        elif "windows" in self.system:
            self.system_drive = os.environ["SYSTEMDRIVE"]
            self.workers_manager = WindowsWorkersManager
            self.system_params = self._get_windows_system_params()
        else:
            msg = "System, {0}, is not recognized?".format(self.system)
            self.log.critical(msg)
            raise WatchmakerError(msg)
        if self.log_dir:
            self.system_params["logdir"] = self.log_dir

    def _get_worker_args(self, arguments, extra_arguments):
        worker_args = arguments

        # Convert extra_arguments to a dict and merge it with worker_args.
        # Leading hypens are removed, and other hyphens are converted to
        # underscores
        worker_args.update(
            dict(
                (k.lstrip("-").replace("-", "_"), v)
                for k, v in zip(*[iter(extra_arguments)] * 2)
            )
        )

        try:
            # Set self.worker_args, removing `None` values from worker_args
            return dict(
                (k, yaml.safe_load("null" if v is None else v))
                for k, v in worker_args.items()
                if v != Arguments.DEFAULT_VALUE
            )
        except yaml.YAMLError as exc:
            if hasattr(exc, "problem_mark"):
                msg = (
                    "Failed to parse argument value as YAML. Check the format "
                    "and/or properly quote the value when using the CLI to "
                    "account for shell interpolation. YAML error: {0}"
                ).format(str(exc))
                self.log.critical(msg)
                raise InvalidValueError(msg)
            raise

    def install(self):
        """
        Execute the watchmaker workers against the system.

        Upon successful execution, the system will be properly provisioned,
        according to the defined configuration and workers.
        """
        self.log.info("Start time: %s", datetime.datetime.now())
        self.log.info("Workers to execute: %s", self.config.keys())

        # Create watchmaker directories
        try:
            os.makedirs(self.system_params["workingdir"])
            oschmod.set_mode(self.system_params["prepdir"], 0o700)
        except OSError:
            if not os.path.exists(self.system_params["workingdir"]):
                msg = "Unable to create directory - {0}".format(
                    self.system_params["workingdir"]
                )
                self.log.critical(msg)
                self.status.update_status("ERROR")
                raise

        workers_manager = self.workers_manager(
            system_params=self.system_params, workers=self.config
        )

        try:
            workers_manager.worker_cadence()
        except Exception:
            msg = "Execution of the workers cadence has failed."
            self.log.critical(msg)
            self.status.update_status("ERROR")
            raise

        if self.no_reboot:
            self.log.info("Detected `no-reboot` switch. \
                           System will not be rebooted.")
        else:
            self.log.info(
                "Reboot scheduled. System will reboot after the script exits."
            )
            subprocess.call(self.system_params["restart"], shell=True)
        self.status.update_status("COMPLETE")
        self.log.info("Stop time: %s", datetime.datetime.now())
