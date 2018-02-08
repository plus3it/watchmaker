# -*- coding: utf-8 -*-
"""Watchmaker logger module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import collections
import errno
import io
import json
import logging
import logging.handlers
import os
import platform
import subprocess
import xml.etree.ElementTree

IS_WINDOWS = platform.system() == 'Windows'
MESSAGE_TYPES = ('Information', 'Warning', 'Error')

HAS_PYWIN32 = False
try:
    import win32evtlog  # noqa: F401
    HAS_PYWIN32 = True
except ImportError:
    pass

EC2_CONFIG_DEPS = False
try:
    import defusedxml.ElementTree
    PROGRAM_FILES = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
    EC2_CONFIG = '\\'.join([
        PROGRAM_FILES,
        'Amazon\\Ec2ConfigService\\Settings\\Config.xml'
    ])
    EC2_CONFIG_EVENT_LOG = '\\'.join([
        PROGRAM_FILES,
        'Amazon\\Ec2ConfigService\\Settings\\EventLogConfig.xml'
    ])
    EC2_CONFIG_DEPS = IS_WINDOWS
except ImportError:
    pass

EC2_LAUNCH_DEPS = False
try:
    PROGRAM_DATA = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
    EC2_LAUNCH_LOG_CONFIG = '\\'.join([
        PROGRAM_DATA,
        'Amazon\\EC2-Windows\\Launch\\Config\\EventLogConfig.json'
    ])
    EC2_LAUNCH_SEND_EVENTS = '\\'.join([
        PROGRAM_DATA,
        'Amazon\\EC2-Windows\\Launch\\Scripts\\SendEventLogs.ps1'
    ])
    assert IS_WINDOWS
    EC2_LAUNCH_DEPS = True
except AssertionError:
    pass

LOG_LEVELS = collections.defaultdict(
    lambda: logging.DEBUG,  # log level if key is not in this dict
    {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }
)


def exception_hook(exc_type, exc_value, exc_traceback):
    """Log unhandled exceptions with hook for sys.excepthook."""
    log = logging.getLogger('watchmaker')
    log.critical(
        '',
        exc_info=(exc_type, exc_value, exc_traceback)
    )


def make_log_dir(log_dir):
    """
    Create logging directory if it does not exist.

    Args:
        log_dir: (:obj:`str`)
        Path to a directory.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


def log_system_details(log):
    """Log details about the system Watchmaker is running on."""
    log.info('System OS: %s', platform.system())
    log.info('System Architecture: %s', platform.architecture())
    log.info('System''s Release: %s', platform.release())
    log.info('System''s Release Version: %s', platform.version())
    log.info('Machine Type: %s', platform.machine())
    log.info('Network Name: %s', platform.node())
    log.info('Processor Name: %s', platform.processor())
    log.info('Python Version: %s', platform.python_version())


def prepare_logging(log_dir, log_level):
    """
    Prepare the logger for handling messages to a file and/or to stdout.

    Args:
        log_dir: (:obj:`str`)
            Path to a directory. If set, Watchmaker logs to a file named
            ``watchmaker.log`` in the specified directory. Both the directory
            and the file will be created if necessary. If the file already
            exists, Watchmaker appends to it rather than overwriting it. If
            this argument evaluates to ``False``, then logging to a file is
            disabled. Watchmaker will always output to stdout/stderr.

        log_level: (:obj:`str`)
            Level to log at. Case-insensitive. Valid options include,
            from least to most verbose:

            - ``critical``
            - ``error``
            - ``warning``
            - ``info``
            - ``debug``
    """
    logformat = (
        '%(asctime)s [%(name)s][%(levelname)-5s][%(process)s]: %(message)s'
    )
    level = LOG_LEVELS[str(log_level).lower()]

    logging.basicConfig(format=logformat, level=level)

    if not log_dir:
        logging.warning(
            'Watchmaker will not be logging to a file!'
        )
    else:
        make_log_dir(log_dir)
        log_filename = os.sep.join((log_dir, 'watchmaker.log'))
        hdlr = logging.FileHandler(log_filename)
        hdlr.setLevel(level)
        hdlr.setFormatter(logging.Formatter(logformat))
        logging.getLogger().addHandler(hdlr)

    if HAS_PYWIN32:
        ehdlr = logging.handlers.NTEventLogHandler('Watchmaker')
        ehdlr.setLevel(level)
        ehdlr.setFormatter(logging.Formatter(logformat))
        logging.getLogger().addHandler(ehdlr)

    if HAS_PYWIN32 and EC2_CONFIG_DEPS:
        try:
            _enable_ec2_config_event_log()
            _configure_ec2_config_event_log()
        except (IOError, OSError) as exc:
            if exc.errno == errno.ENOENT:
                # PY2/PY3-compatible check for FileNotFoundError
                # EC2_CONFIG or EC2_LOG_CONFIG do not exist
                pass
            else:
                raise

    if HAS_PYWIN32 and EC2_LAUNCH_DEPS:
        try:
            _configure_ec2_launch_event_log()
            _schedule_ec2_launch_event_log()
        except (IOError, OSError) as exc:
            if exc.errno == errno.ENOENT:
                # PY2/PY3-compatible check for FileNotFoundError
                # EC2_LAUNCH_LOG_CONFIG or 'powershell.exe' do not exist
                pass
            else:
                raise
        except subprocess.CalledProcessError:
            # EC2_LAUNCH_SEND_EVENTS does not exist
            pass


def _enable_ec2_config_event_log():
    """Enable EC2Config forwarding of Event Logs to EC2 System Log."""
    ec2_config = xml.etree.ElementTree.ElementTree(
        xml.etree.ElementTree.Element('Ec2ConfigurationSettings'))

    with io.open(EC2_CONFIG) as fh_:
        ec2_config = defusedxml.ElementTree.parse(
            fh_,
            forbid_dtd=True
        )

    plugins = ec2_config.getroot().find('Plugins').findall('Plugin')
    for plugin in plugins:
        if plugin.find('Name').text == 'Ec2EventLog':
            plugin.find('State').text = 'Enabled'
            break

    with io.open(EC2_CONFIG, mode='wb') as fh_:
        ec2_config.write(fh_)


def _configure_ec2_config_event_log():
    """Configure EC2Config to forward Event Log entries for Watchmaker."""
    ec2_log_config = xml.etree.ElementTree.ElementTree(
        xml.etree.ElementTree.Element('EventLogConfig'))

    with io.open(EC2_CONFIG_EVENT_LOG) as fh_:
        ec2_log_config = defusedxml.ElementTree.parse(
            fh_,
            forbid_dtd=True
        )

    events_present = set()
    events = ec2_log_config.getroot().findall('Event')
    # Check if the event is already present
    for event in events:
        if (
            event.find('ErrorType').text in MESSAGE_TYPES and
            event.find('Category').text == 'Application' and
            event.find('AppName').text == 'Watchmaker'
        ):
            events_present.add(event.find('ErrorType').text)

    # Add missing events
    events_missing = events_present.symmetric_difference(MESSAGE_TYPES)
    for msg_type in events_missing:
        event = xml.etree.ElementTree.SubElement(
            ec2_log_config.getroot(),
            'Event',
            {}
        )
        category = xml.etree.ElementTree.SubElement(
            event,
            'Category',
            {}
        )
        error_type = xml.etree.ElementTree.SubElement(
            event,
            'ErrorType',
            {}
        )
        num_entries = xml.etree.ElementTree.SubElement(
            event,
            'NumEntries',
            {}
        )
        last_message_time = xml.etree.ElementTree.SubElement(
            event,
            'LastMessageTime',
            {}
        )
        app_name = xml.etree.ElementTree.SubElement(
            event,
            'AppName',
            {}
        )
        category.text = 'Application'
        error_type.text = msg_type
        num_entries.text = '999999'
        last_message_time.text = '2008-09-10T00:00:00.000Z'
        app_name.text = 'Watchmaker'

    if events_missing:
        with io.open(EC2_CONFIG_EVENT_LOG, mode='wb') as fh_:
            ec2_log_config.write(fh_)


def _configure_ec2_launch_event_log():
    """Configure EC2Launch to forward Event Log entries for Watchmaker."""
    event_config = {}
    with io.open(EC2_LAUNCH_LOG_CONFIG) as fh_:
        event_config = json.load(fh_)

    events_present = set()
    events = event_config.get('events', [])
    # Check if the event is already present
    for event in events:
        if (
            event.get('level') in MESSAGE_TYPES and
            event.get('logName') == 'Application' and
            event.get('source') == 'Watchmaker'
        ):
            events_present.add(event.get('level'))

    # Add missing events
    events_missing = events_present.symmetric_difference(MESSAGE_TYPES)
    for msg_type in events_missing:
        event = {
            'logName': 'Application',
            'source': 'Watchmaker',
            'level': msg_type,
            'numEntries': '999'
        }
        events += [event]

    if events_missing:
        event_config['events'] = events
        with io.open(EC2_LAUNCH_LOG_CONFIG, mode='w') as fh_:
            json.dump(event_config, fh_, indent=4)


def _schedule_ec2_launch_event_log():
    """Schedule EC2Launch to forward Event Logs to EC2 System Log."""
    return subprocess.check_call([
        'powershell.exe',
        '-NoLogo',
        '-NoProfile',
        '-NonInteractive',
        '-ExecutionPolicy',
        'Bypass',
        EC2_LAUNCH_SEND_EVENTS,
        '-Schedule',
        '| out-null'
    ])
