import logging
import sys


def SystemFatal(msg):
    """
    This is a temporary exception handler for the project.

    Args:
        msg (str):
            Message for logging and stdout.

    Returns:
        Exits with error code 1
    """
    print(msg)
    logging.critical(msg)
    sys.exit(1)
