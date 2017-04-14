# -*- coding: utf-8 -*-
"""Watchmaker workers manager."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from watchmaker.managers.base import WorkersManagerBase
from watchmaker.workers.salt import SaltLinux, SaltWindows
from watchmaker.workers.yum import Yum


class LinuxWorkersManager(WorkersManagerBase):
    """Manage the worker cadence for Linux systems."""

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def worker_cadence(self):
        """Manage worker cadence."""
        for worker in self.workers:
            configuration = self.workers[worker]['config']
            if 'yum' in worker:
                yum = Yum(
                    system_params=self.system_params,
                    **configuration
                )
                yum.install()
            elif 'salt' in worker:
                salt = SaltLinux(
                    system_params=self.system_params,
                    **configuration
                )
                salt.install()

    def cleanup(self):
        """Execute cleanup function."""
        pass


class WindowsWorkersManager(WorkersManagerBase):
    """Manage the worker cadence for Windows systems."""

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def worker_cadence(self):
        """Manage worker cadence."""
        for worker in self.workers:
            configuration = self.workers[worker]['config']
            if 'salt' in worker:
                salt = SaltWindows(
                    system_params=self.system_params,
                    **configuration
                )
                salt.install()

    def cleanup(self):
        """Execute cleanup function."""
        pass
