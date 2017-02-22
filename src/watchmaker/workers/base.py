# -*- coding: utf-8 -*-
"""Watchmaker base worker."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from watchmaker.managers.base import LinuxManager


class Generic(LinuxManager):
    """Generic worker class for additional User configurated support."""

    def __init__(self):  # noqa: D102
        super(Generic, self).__init__()
