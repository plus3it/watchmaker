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
        system_params (:obj:`dict`):
            Attributes, mostly file-paths, specific to the Linux system-type.
        execution_scripts (:obj:`dict`):
            Workers to run and associated configuration data.
    """

    def __init__(self, system_params, execution_scripts):  # noqa: D102
        super(LinuxWorkersManager, self).__init__()
        self.execution_scripts = execution_scripts
        self.manager = LinuxManager()
        self.system_params = system_params

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
                salt.install(configuration)

    def cleanup(self):
        """Execute cleanup function."""
        self.manager.cleanup()


class WindowsWorkersManager(WorkersManagerBase):
    """
    Manage the worker cadence for Windows systems.

    Args:
        system_params (:obj:`dict`):
            Attributes, mostly file-paths, specific to the Windows system-type.
        execution_scripts (:obj:`dict`):
            Workers to run and associated configuration data.
    """

    def __init__(self, system_params, execution_scripts):  # noqa: D102
        super(WindowsWorkersManager, self).__init__()
        self.execution_scripts = execution_scripts
        self.manager = WindowsManager()
        self.system_params = system_params

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
                salt.install(configuration)

    def cleanup(self):
        """Execute cleanup function."""
        self.manager.cleanup()
