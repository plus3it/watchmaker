"""Watchmaker base worker."""


import abc
import logging


class WorkerBase:
    """Define the architecture of a Worker."""

    def __init__(self, system_params, *args, **kwargs):
        self.log = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )

        self.system_params = system_params
        WorkerBase.args = args
        WorkerBase.kwargs = kwargs

    @abc.abstractmethod
    def before_install(self):
        """Add before_install method to all child classes."""
        pass

    @abc.abstractmethod
    def install(self):
        """Add install method to all child classes."""
        pass
