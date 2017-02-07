# -*- coding: utf-8 -*-
"""Watchmaker workers manager."""
import json

from watchmaker.managers.base import (LinuxManager, WindowsManager,
                                      WorkersManagerBase)
from watchmaker.workers.salt import SaltLinux, SaltWindows
from watchmaker.workers.yum import Yum


class LinuxWorkersManager(WorkersManagerBase):
    """Manage the worker cadence for Linux systems."""

    def __init__(self, *args, **kwargs):  # noqa: D102
        super(LinuxWorkersManager, self).__init__(*args, **kwargs)
        self.manager = LinuxManager()

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def worker_cadence(self):
        """Manage worker cadence."""
        for worker in self.workers:
            configuration = json.dumps(
                self.workers[worker]['Parameters']
            )

            if 'Yum' in worker:
                yum = Yum()
                yum.install(configuration)
            elif 'Salt' in worker:
                salt = SaltLinux()
                salt.install(configuration)

    def cleanup(self):
        """Execute cleanup function."""
        self.manager.cleanup()


class WindowsWorkersManager(WorkersManagerBase):
    """Manage the worker cadence for Windows systems."""

    def __init__(self, *args, **kwargs):  # noqa: D102
        super(WindowsWorkersManager, self).__init__(*args, **kwargs)
        self.manager = WindowsManager()

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def worker_cadence(self):
        """Manage worker cadence."""
        for worker in self.workers:
            configuration = json.dumps(
                self.workers[worker]['Parameters']
            )

            if 'Salt' in worker:
                salt = SaltWindows()
                salt.install(configuration)

    def cleanup(self):
        """Execute cleanup function."""
        self.manager.cleanup()
