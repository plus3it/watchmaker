#!/usr/bin/env python
import argparse

from watchmaker import Prepare

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--noreboot', dest='noreboot', action='store_true')
    parser.add_argument('--sourceiss3bucket', dest='sourceiss3bucket', action='store_true')
    parser.add_argument('--config', dest='config', default='config.yaml')
    parser.add_argument('--logger', dest='logger', action='store_true')
    parser.add_argument('--log-path', dest='log_path', default='.')

    systemprep = Prepare(parser.parse_args().noreboot,
                            parser.parse_args().sourceiss3bucket,
                            parser.parse_args().config,
                            parser.parse_args().logger,
                            parser.parse_args().log_path)
    systemprep.install_system()





