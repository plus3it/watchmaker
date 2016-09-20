import argparse

from watchmaker import Prepare
from watchmaker.logger import prepare_logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--noreboot', dest='noreboot', action='store_true',
                        help='No reboot after provisioning.')
    parser.add_argument('--sourceiss3bucket', dest='sourceiss3bucket',
                        action='store_true',
                        help=(
                            'Use S3 buckets instead of internet locations for '
                            'files.'
                        ))
    parser.add_argument('--config', dest='config', default=None,
                        help='Path or URL to the config.yaml file.')
    parser.add_argument('--saltstates', dest='saltstates', default=None,
                        help=(
                            'Define the saltstates to use.  Must be None, '
                            'Highstate, or a comma-separated-string'
                        ))
    parser.add_argument('--log-dir', dest='log_dir', default=None,
                        help='Path to the log directory for logging.'
                        )
    parser.add_argument('-v', action='count', dest='verbosity', default=0)

    arguments = parser.parse_args()
    prepare_logging(arguments.log_dir, arguments.verbosity)

    systemprep = Prepare(arguments)
    systemprep.install_system()
