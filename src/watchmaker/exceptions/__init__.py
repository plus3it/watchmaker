import logging
import sys


class ExcLevel:
    Error = 1
    Critical = 2


def wm_exit(message, level):
    if level == ExcLevel.Error:
        logging.error(message, exc_info=True)

    if level == ExcLevel.Critical:
        logging.critical(message, exc_info=True)

    sys.exit(1)
