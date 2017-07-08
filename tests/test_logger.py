# -*- coding: utf-8 -*-
"""Watchmaker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging
import os
import shutil
import sys

import pytest

from watchmaker.logger import (LOG_LEVELS, exception_hook, make_log_dir,
                               prepare_logging)


def test_log_level_dict():
    """Tests the LOG_LEVELS dict."""
    # Test strings that are in the dict.
    level = LOG_LEVELS['critical']
    assert level == logging.CRITICAL
    level = LOG_LEVELS['debug']
    assert level == logging.DEBUG

    # Test that a string not in dict will return logging.DEBUG.
    level = LOG_LEVELS['lalaland']
    assert level == logging.DEBUG


def test_making_log_directory():
    """Tests creation of a directory if it does not exist."""
    log_dir = './logfiles/'
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)

    # Make sure that directory is created.
    make_log_dir(log_dir)
    assert os.path.exists(log_dir)

    # Checks that path still exists without throwing error.
    # I.e. don't try to create the directory again.
    make_log_dir(log_dir)
    assert os.path.exists(log_dir)


@pytest.mark.skipif(sys.version_info < (2, 7),
                    reason="Not supported in this Python version.")
def test_logger_handler():
    """
    Tests prepare_logging() use case.

    Tests that prepare_logging() will set logger level appropriately
    and attach a FileHandler if a directory is passed.
    """
    prepare_logging('./logfiles', 'debug')
    logger = logging.getLogger()
    log_hdlr = logger.handlers.pop()
    assert type(log_hdlr) == logging.FileHandler
    assert log_hdlr.level == logging.DEBUG


def test_log_if_no_log_directory_given(caplog):
    """
    Tests prepare_logging() use case.

    Tests that not passing in a path to a logging directory will
    produce a logging message.
    """
    prepare_logging(None, 'info')
    assert 'Watchmaker will not be logging to a file!' in caplog.text()


def test_exception_hook(caplog):
    """Tests that exception_hook() will produce a logging message."""
    rte = RuntimeError('Test Error')
    exception_hook(type(rte), rte, None)
    record = caplog.records()[0]
    assert record.levelname == 'CRITICAL'
    assert record.name == 'watchmaker'
    assert 'RuntimeError: Test Error' in caplog.text()
