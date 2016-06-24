import sys
import logging

def SystemFatal(msg):
    """
    This is a temporary exception handler for the project.  It will be reworked in the future.

    :param msg: Message for logging and stdout.

    :return: Exits with error code 1
    """

    print(msg)
    logging.error(msg)
    sys.exit(1)

