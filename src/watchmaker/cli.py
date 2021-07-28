# -*- coding: utf-8 -*-
"""Watchmaker cli."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import platform
import sys

import click

import watchmaker
from watchmaker.logger import LOG_LEVELS, exception_hook, prepare_logging

click.disable_unicode_literals_warning = True

LOG_LOCATIONS = {
    'linux': os.path.sep.join(('', 'var', 'log', 'watchmaker')),
    'windows': os.path.sep.join((
        os.environ.get('SYSTEMDRIVE', 'C:'), 'Watchmaker', 'Logs'))
}


def _print_version(ctx, _param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(watchmaker.VERSION_INFO)
    ctx.exit()


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option(
    '--version', is_flag=True, callback=_print_version, expose_value=False,
    is_eager=True)
@click.option(
    '-c', '--config', 'config_path', default=None, show_default=True,
    help=(
        'Path or URL to the config.yaml file. If not set, watchmaker will use '
        'its default config.'))
@click.option(
    '-l', '--log-level', default='debug', show_default=True,
    type=click.Choice(list(LOG_LEVELS.keys())),
    help='Set the log level. Case-insensitive.')
@click.option(
    '-d', '--log-dir', show_default=True,
    type=click.Path(exists=False, file_okay=False),
    default=LOG_LOCATIONS.get(platform.system().lower(), None),
    help=(
        'Path to the directory where Watchmaker log files will be '
        'saved.'))
@click.option(
    '-n', '--no-reboot', 'no_reboot', flag_value=True, default=False,
    show_default=True,
    help=(
        'If this flag is not passed, Watchmaker will reboot the '
        'system upon success. This flag suppresses that behavior. '
        'Watchmaker suppresses the reboot automatically if it '
        'encounters a failure.'))
@click.option(
    '-s', '--salt-states', default=None, show_default=True,
    help=(
        'Comma-separated string of salt states to apply. A value of '
        '\'none\' will not apply any salt states. A value of '
        '\'highstate\' will apply the salt highstate.'))
@click.option(
    '-A', '--admin-groups', default=None, show_default=True,
    help=(
        'Set a salt grain that specifies the domain groups that '
        'should have root privileges on Linux or admin privileges '
        'on Windows. Value must be a colon-separated string. E.g. '
        '"group1:group2"'))
@click.option(
    '-a', '--admin-users', default=None, show_default=True,
    help=(
        'Set a salt grain that specifies the domain users that '
        'should have root privileges on Linux or admin privileges '
        'on Windows. Value must be a colon-separated string. E.g. '
        '"user1:user2"'))
@click.option(
    '-t', '--computer-name', default=None, show_default=True,
    help=(
        'Set a salt grain that specifies the computername to apply '
        'to the system.'))
@click.option(
    '-e', '--env', 'environment', default=None, show_default=True,
    help=(
        'Set a salt grain that specifies the environment in which '
        'the system is being built. E.g. dev, test, or prod'))
@click.option(
    '-p', '--ou-path', default=None, show_default=True,
    help=(
        'Set a salt grain that specifies the full DN of the OU '
        'where the computer account will be created when joining a '
        'domain. E.g. "OU=SuperCoolApp,DC=example,DC=com"'))
@click.argument('extra_arguments', nargs=-1, type=click.UNPROCESSED,
                metavar='')
def main(extra_arguments=None, **kwargs):
    """Entry point for Watchmaker cli."""
    prepare_logging(kwargs['log_dir'], kwargs['log_level'])

    sys.excepthook = exception_hook

    watchmaker_arguments = watchmaker.Arguments(**dict(
        extra_arguments=extra_arguments,
        **kwargs
    ))
    watchmaker_client = watchmaker.Client(watchmaker_arguments)
    sys.exit(watchmaker_client.install())
