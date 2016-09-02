import datetime
import logging
import os
import sys


class LogHandler:
    def __init__(self, log_dir, log_level):
        """
        Prepares the logger for handling messages to a file and/or to stdout.
        Args:
            log_dir (str):
                Path of a directory. If this object is not None, then this
                directory will be used to store a log file.
        """
        logformat = '[%(asctime)s] %(levelname)s:\t%(message)s'
        if log_level == 0 or log_level == 1:
            level = logging.WARNING
        elif log_level == 2:
            level = logging.INFO
        else:
            level = logging.DEBUG

        logging.basicConfig(format=logformat, level=level)

        if not log_dir:
            logging.getLogger('Prepare').warning(
                'Watchmaker will not be logging to a file!'
            )
        elif os.path.isfile(log_dir):
            logging.getLogger('Prepare').error(
                'Log directory passed in is a file. Pass in a directory.'
            )
            sys.exit(1)
        else:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_filename = os.sep.join((
                log_dir,
                'watchmaker-{0}.log'.format(str(datetime.date.today()))
            ))
            hdlr = logging.FileHandler(log_filename)
            hdlr.setLevel(level)
            hdlr.setFormatter(logging.Formatter(logformat))
            logging.getLogger('Prepare').addHandler(hdlr)
