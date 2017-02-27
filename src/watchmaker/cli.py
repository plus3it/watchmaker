# -*- coding: utf-8 -*-
"""Watchmaker cli."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import argparse
import os
import sys

import watchmaker
from watchmaker.logger import prepare_logging


def _validate_log_dir(log_dir):
    if os.path.isfile(log_dir):
        raise argparse.ArgumentTypeError(
            '"{0}" exists as a file.'.format(log_dir)
        )
    return log_dir


def main():
    """Entry point for Watchmaker cli."""
    version_string = 'watchmaker v{0}'.format(watchmaker.__version__)

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=version_string,
                        help='Print version info.')
    parser.add_argument('-v', '--verbose', action='count', dest='verbosity',
                        default=0,
                        help=(
                            'Enable verbose logging: -v for INFO, -vv to '
                            'include DEBUG, if option is left out, only '
                            'WARNINGS and higher are logged.'
                        ))
    parser.add_argument('-c', '--config', dest='config_path', default=None,
                        help='Path or URL to the config.yaml file.')
    parser.add_argument('-n', '--no-reboot', dest='no_reboot',
                        action='store_true',
                        help=(
                            'If this flag is not passed, Watchmaker will '
                            'reboot the system upon success. This flag '
                            'suppresses that behavior. Watchmaker suppresses '
                            'the reboot automatically if it encounters a'
                            'failure.'
                        ))
    parser.add_argument('-l', '--log-dir', dest='log_dir', default=None,
                        type=_validate_log_dir,
                        help='Path to the log directory for logging.'
                        )
    parser.add_argument('--s3-source', dest='s3_source',
                        action='store_const', const=True, default=None,
                        help=(
                            'Use S3 utilities to retrieve content instead of '
                            'http/s utilities.'
                        ))
    parser.add_argument('-s', '--salt-states', dest='salt_states',
                        default=None,
                        help=(
                            'Comma-separated string of salt states to apply. '
                            'A value of \'None\' will not apply any salt '
                            'states. A value of \'Highstate\' will apply the '
                            'salt highstate.'
                        ))
    parser.add_argument('-A', '--admin-groups', dest='admin_groups',
                        default=None,
                        help=(
                            'Set a salt grain that specifies the domain '
                            'groups that should have root privileges on Linux '
                            'or admin privileges on Windows. Value must be a '
                            'colon-separated string. E.g. "group1:group2"'
                        ))
    parser.add_argument('-a', '--admin-users', dest='admin_users',
                        default=None,
                        help=(
                            'Set a salt grain that specifies the domain users '
                            'that should have root privileges on Linux or '
                            'admin privileges on Windows. Value must be a '
                            'colon-separated string. E.g. "user1:user2"'
                        ))
    parser.add_argument('-t', '--computer-name', dest='computer_name',
                        default=None,
                        help=(
                            'Set a salt grain that specifies the computername '
                            'to apply to the system.'
                        ))
    parser.add_argument('-e', '--env', dest='environment', default=None,
                        help=(
                            'Set a salt grain that specifies the environment '
                            'in which the system is being built. E.g. dev, '
                            'test, or prod'
                        ))
    parser.add_argument('-p', '--ou-path', dest='ou_path', default=None,
                        help=(
                            'Set a salt grain that specifies the full DN of '
                            'the OU where the computer account will be '
                            'created when joining a domain. E.g. '
                            '"OU=SuperCoolApp,DC=example,DC=com"'
                        ))

    arguments, extra_arguments = parser.parse_known_args()
    prepare_logging(arguments.log_dir, arguments.verbosity)

    watchmaker_arguments = watchmaker.Arguments(**dict(
        extra_arguments=extra_arguments,
        **vars(arguments)
    ))
    watchmaker_client = watchmaker.Client(watchmaker_arguments)
    sys.exit(watchmaker_client.install())
