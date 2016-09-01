import datetime
import logging
import os
import sys


class LogHandler:
    def __init__(self):
        pass

    @staticmethod
    def prepare_logger(log_dir, log_file):
        """
        Prepares the logger for handling messages to a file and/or to stdout.
        Args:
            log_dir (str):
                Path of a directory. If this object is not None, then this
                directory will be used to store a log file.
            log_file (str):
                Path to a file. If this object is not None, then this path
                to a file will be used as the log file.
        """
        log_filename = None
        if log_dir and os.path.exists(log_dir):
            if os.path.isfile(log_dir):
                log_msg = '{0} is a file and not a directory.'.format(log_dir)
                log_type = 'error'
            else:
                log_filename = os.path.join(
                    log_dir,
                    'watchmaker-{0}.log'.format(str(datetime.date.today()))
                )
                log_msg = 'Start time: {0}'.format(datetime.datetime.now())
                log_type = 'info'
        elif log_file:
            if os.path.isdir(log_file):
                log_msg = '{0} is a directory and not a file.'.format(log_file)
                log_type = 'error'
            else:
                log_filename = log_file
                log_msg = 'Start time: {0}'.format(datetime.datetime.now())
                log_type = 'info'
        elif not log_dir and not log_file:
            log_msg = 'Watchmaker will not be logging to a file!'
            log_type = 'warning'
        else:
            log_msg = '{0} does not exist'.format(log_dir)
            log_type = 'error'

        if log_filename:
            logging.basicConfig(
                filename=log_filename,
                format='%(levelname)s:\t%(message)s',
                level=logging.DEBUG
            )
        else:
            logging.basicConfig()

        getattr(logging, log_type)(log_msg)

    @staticmethod
    def add(msg, log_type='info', exc=None):
        getattr(logging, log_type)(msg)
        if log_type == 'critical':
            sys.exit(1)
        if exc:
            raise SystemError(msg, exc)
