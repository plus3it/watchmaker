# -*- coding: utf-8 -*-
"""Watchmaker workers manager."""
import json

from watchmaker.managers.base import (LinuxManager, WindowsManager,
                                      WorkersManagerBase)
from watchmaker.workers.salt import SaltLinux, SaltWindows
from watchmaker.workers.yum import Yum


class LinuxWorkersManager(WorkersManagerBase):
    """
    Manage the worker cadence for Linux systems.

    Args:
        s3 (bool):
            Switch to determine whether to use boto to download files.
        system_params (dict):
            Attributes, mostly file-paths, specific to the Linux system-type.
        execution_scripts (dict):
            Workers to run and associated configuration data.
        salt_states (str):
            Comma-separated string of salt states to execute. Accepts two
            special keywords:

            - ``'None'``: Do not apply any salt states
            - ``'Highstate'``: Apply the salt highstate
    """

    def __init__(self, s3, system_params, execution_scripts, salt_states
    ):  # noqa: D102
        super(LinuxWorkersManager, self).__init__()
        self.execution_scripts = execution_scripts
        self.manager = LinuxManager()
        self.is_s3_bucket = s3
        self.system_params = system_params
        self.salt_states = salt_states

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def worker_cadence(self):
        """Manage worker cadence."""
        for script in self.execution_scripts:
            configuration = json.dumps(
                self.execution_scripts[script]['Parameters']
            )

            if 'Yum' in script:
                yum = Yum()
                yum.install(configuration)
            elif 'Salt' in script:
                salt = SaltLinux()
                salt.install(
                    configuration,
                    self.is_s3_bucket,
                    self.salt_states
                )

    def cleanup(self):
        """Execute cleanup function."""
        self.manager.cleanup()


class WindowsWorkersManager(WorkersManagerBase):
    """
    Manage the worker cadence for Windows systems.

    Args:
        s3 (bool):
            Switch to determine whether to use boto to download files.
        system_params (dict):
            Attributes, mostly file-paths, specific to the Windows system-type.
        execution_scripts (dict):
            Workers to run and associated configuration data.
        salt_states (str):
            Comma-separated string of salt states to execute. Accepts two
            special keywords:

            - ``'None'``: Do not apply any salt states
            - ``'Highstate'``: Apply the salt highstate
    """

    def __init__(self, s3, system_params, execution_scripts, salt_states
    ):  # noqa: D102
        super(WindowsWorkersManager, self).__init__()
        self.execution_scripts = execution_scripts
        self.manager = WindowsManager()
        self.is_s3_bucket = s3
        self.system_params = system_params
        self.salt_states = salt_states

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def worker_cadence(self):
        """Manage worker cadence."""
        for script in self.execution_scripts:
            configuration = json.dumps(
                self.execution_scripts[script]['Parameters']
            )

            if 'Salt' in script:
                salt = SaltWindows()
                salt.install(
                    configuration,
                    self.is_s3_bucket,
                    self.salt_states
                )

    def cleanup(self):
        """Execute cleanup function."""
        self.manager.cleanup()
