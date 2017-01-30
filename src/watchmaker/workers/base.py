# -*- coding: utf-8 -*-
from watchmaker.managers.base import LinuxManager


class Generic(LinuxManager):
    """
    Generic worker class for additional User configurated support.
    """

    def __init__(self):
        super(Generic, self).__init__()
