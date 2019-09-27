# -*- coding: utf-8 -*-
"""Watchmaker base worker."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import abc
import logging


class WorkerBase(object):
    """Define the architecture of a Worker."""

    def __init__(self, system_params, *args, **kwargs):
        self.log = logging.getLogger(
            '{0}.{1}'.format(__name__, self.__class__.__name__)
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
