# -*- coding: utf-8 -*-
"""Watchmaker logger module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import collections
import logging
import os

LOG_LEVELS = collections.defaultdict(
    lambda: logging.DEBUG,  # log level if key is not in this dict
    {
        0: logging.WARNING,
        1: logging.INFO
    }
)


def prepare_logging(log_dir, log_level):
    """
    Prepare the logger for handling messages to a file and/or to stdout.

    Args:
        log_dir (:obj:`str`):
            Path to a directory. If set, Watchmaker logs to the
            ``watchmaker.log`` file in the specified directory. Both the
            directory and the file will be created if necessary. If the file
            already exists, Watchmaker appends to it rather than overwriting
            it. If this argument evaluates to ``False``, then logging to a file
            is disabled. Watchmaker will always output to stdout/stderr.
        log_level (int):
            Level to log at. Any value other than the integers below will
            enable DEBUG logging.

            .. code-block:: python

                0: WARNING
                1: INFO
                *: DEBUG
    """
    logformat = (
        '%(asctime)s [%(name)s][%(levelname)-5s][%(process)s]: %(message)s'
    )
    level = LOG_LEVELS[log_level]

    logging.basicConfig(format=logformat, level=level)

    if not log_dir:
        logging.warning(
            'Watchmaker will not be logging to a file!'
        )
    else:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_filename = os.sep.join((log_dir, 'watchmaker.log'))
        hdlr = logging.FileHandler(log_filename)
        hdlr.setLevel(level)
        hdlr.setFormatter(logging.Formatter(logformat))
        logging.getLogger().addHandler(hdlr)
