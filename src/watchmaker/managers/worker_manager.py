"""Workers Manager module."""

import abc
from typing import ClassVar

from watchmaker.workers.salt import SaltLinux, SaltWindows
from watchmaker.workers.yum import Yum


class WorkersManagerBase(metaclass=abc.ABCMeta):
    """
    Base class for worker managers.

    Args:
        system_params: (:obj:`dict`)
            Attributes, mostly file-paths, specific to the system-type (Linux
            or Windows).

        workers: (:obj:`collections.OrderedDict`)
            Workers to run and associated configuration data.

    """

    WORKERS: ClassVar[dict] = {}

    def __init__(self, system_params, workers, *args, **kwargs):
        self.system_params = system_params
        self.workers = workers
        WorkersManagerBase.args = args
        WorkersManagerBase.kwargs = kwargs

    @abc.abstractmethod
    def _worker_execution(self):
        pass

    @abc.abstractmethod
    def _worker_validation(self):
        pass

    def worker_cadence(self):
        """Manage worker cadence."""
        workers = []

        for worker, items in self.workers.items():
            configuration = items["config"]
            workers.append(
                self.WORKERS.get(worker)(
                    system_params=self.system_params,
                    **configuration,
                ),
            )

        for worker in workers:
            worker.before_install()

        for worker in workers:
            worker.install()

    @abc.abstractmethod
    def cleanup(self):  # noqa: D102
        pass


class LinuxWorkersManager(WorkersManagerBase):
    """Manage the worker cadence for Linux systems."""

    WORKERS: ClassVar[dict] = {"yum": Yum, "salt": SaltLinux}

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def cleanup(self):
        """Execute cleanup function."""


class WindowsWorkersManager(WorkersManagerBase):
    """Manage the worker cadence for Windows systems."""

    WORKERS: ClassVar[dict] = {"salt": SaltWindows}

    def _worker_execution(self):
        pass

    def _worker_validation(self):
        pass

    def cleanup(self):
        """Execute cleanup function."""
