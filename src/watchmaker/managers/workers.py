# -*- coding: utf-8 -*-
"""Watchmaker workers manager."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from watchmaker.managers.base import WorkersManagerBase
from watchmaker.workers.salt import SaltLinux, SaltWindows
from watchmaker.workers.yum import Yum


class LinuxWorkersManager(WorkersManagerBase):
    """Manage the worker cadence for Linux systems."""

    WORKERS = {
        'yum': Yum,
        'salt': SaltLinux
    }

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def cleanup(self):
        """Execute cleanup function."""
        pass


class WindowsWorkersManager(WorkersManagerBase):
    """Manage the worker cadence for Windows systems."""

    WORKERS = {
        'salt': SaltWindows
    }

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def cleanup(self):
        """Execute cleanup function."""
        pass
