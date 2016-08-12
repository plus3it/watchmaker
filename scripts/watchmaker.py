#!/usr/bin/env python
import argparse

from watchmaker import Prepare

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--noreboot', dest='noreboot', action='store_true',
                        help='No reboot after provisioning.')
    parser.add_argument('--sourceiss3bucket', dest='sourceiss3bucket', action='store_true',
                        help='Use S3 buckets instead of internet locations for files.')
    parser.add_argument('--config', dest='config', default='config.yaml',
                        help='Path to the config.yaml file.')
    parser.add_argument('--logger', dest='logger', action='store_true', default=False,
                        help='Use stream logger for debugging.')
    parser.add_argument('--log-path', dest='log_path', default=None,
                        help='Path to the logfile for stream logging.')
    parser.add_argument('--saltstates', dest='saltstates', default=None,
                        help='Define the saltstates to use.  Must be None, Highstate, or comma-seperated-string')

    if parser.parse_args().saltstates:
        if parser.parse_args().saltstates.lower() not in ['None'.lower(),
                                                          'Highstate'.lower(),
                                                          'comma-separated-string'.lower()]:
            parser.print_help()

    systemprep = Prepare(parser.parse_args())
    systemprep.install_system()





