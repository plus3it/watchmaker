import logging
import sys


class ExcLevel:
    Error = 1
    Critical = 2


def wm_exit(message, level, has_exc):
    if level == ExcLevel.Error:
        logging.error(message, exc_info=has_exc)

    if level == ExcLevel.Critical:
        logging.critical(message, exc_info=has_exc)

    sys.exit(1)
