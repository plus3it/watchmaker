import logging
import os

from watchmaker.exceptions import ExcLevel
from watchmaker.exceptions import wm_exit


def prepare_logging(log_dir, log_level):
    """
    Prepares the logger for handling messages to a file and/or to stdout.
    Args:
        log_dir (str):
            Path of a directory. If this object is not None, then this
            directory will be used to store a log file.
    """
    logformat = '[%(asctime)s] %(levelname)s: %(message)s'
    if log_level == 0:
        level = logging.WARNING
    elif log_level == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(format=logformat, level=level)

    if not log_dir:
        logging.warning(
            'Watchmaker will not be logging to a file!'
        )
    elif os.path.isfile(log_dir):
        wm_exit(
            'Log directory passed in is a file. Pass in a directory.',
            ExcLevel.Error, False
        )
    else:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_filename = os.sep.join((log_dir, 'watchmaker.log'))
        hdlr = logging.FileHandler(log_filename)
        hdlr.setLevel(level)
        hdlr.setFormatter(logging.Formatter(logformat))
        logging.getLogger().addHandler(hdlr)
