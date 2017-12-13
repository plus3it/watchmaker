# -*- coding: utf-8 -*-
"""Watchmaker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import json
import logging
import logging.handlers
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree

import pytest

from watchmaker import logger


def _pytest_stringify_write_calls(calls, delim='', encoding='utf-8'):
    # Joins the pytest call objects into a string. Each write call contains a
    # single positional argument. x[0][0] retrieves that value. For details on
    # call tuples:
    # https://docs.python.org/3.3/library/unittest.mock.html#calls-as-tuples
    try:
        # Calls are bytes
        return delim.join(x[0][0].decode(encoding) for x in calls)
    except AttributeError:
        # Calls are strings
        return delim.join(x[0][0] for x in calls)


def test_log_level_dict():
    """Tests the LOG_LEVELS dict."""
    # Test strings that are in the dict.
    level = logger.LOG_LEVELS['critical']
    assert level == logging.CRITICAL
    level = logger.LOG_LEVELS['debug']
    assert level == logging.DEBUG

    # Test that a string not in dict will return logging.DEBUG.
    level = logger.LOG_LEVELS['lalaland']
    assert level == logging.DEBUG


def test_making_log_directory():
    """Tests creation of a directory if it does not exist."""
    log_dir = './logfiles/'
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)

    # Make sure that directory is created.
    logger.make_log_dir(log_dir)
    assert os.path.exists(log_dir)

    # Checks that path still exists without throwing error.
    # I.e. don't try to create the directory again.
    logger.make_log_dir(log_dir)
    assert os.path.exists(log_dir)


@pytest.mark.skipif(sys.version_info < (2, 7),
                    reason="Not supported in this Python version.")
def test_logger_handler():
    """
    Tests prepare_logging() use case.

    Tests that prepare_logging() will set logger level appropriately
    and attach a FileHandler if a directory is passed.
    """
    logger.prepare_logging('./logfiles', 'debug')
    this_logger = logging.getLogger()

    if logger.HAS_PYWIN32:
        log_hdlr = this_logger.handlers.pop()
        assert type(log_hdlr) == logging.handlers.NTEventLogHandler
        assert log_hdlr.level == logging.DEBUG

    log_hdlr = this_logger.handlers.pop()
    assert type(log_hdlr) == logging.FileHandler
    assert log_hdlr.level == logging.DEBUG


def test_log_if_no_log_directory_given(caplog):
    """
    Tests prepare_logging() use case.

    Tests that not passing in a path to a logging directory will
    produce a logging message.
    """
    logger.prepare_logging(None, 'info')
    assert 'Watchmaker will not be logging to a file!' in caplog.text


def test_exception_hook(caplog):
    """Tests that exception_hook() will produce a logging message."""
    rte = RuntimeError('Test Error')
    logger.exception_hook(type(rte), rte, None)
    record = caplog.records[0]
    assert record.levelname == 'CRITICAL'
    assert record.name == 'watchmaker'
    assert 'RuntimeError: Test Error' in caplog.text


###
# EC2Config Tests
###
@pytest.mark.skipif(not logger.EC2_CONFIG_DEPS,
                    reason="EC2Config requirements not met.")
@pytest.mark.skipif(sys.version_info < (3,),
                    reason="Not supported in this Python version.")
def test_enable_ec2_config_event_log_raises_filenotfound(mocker):
    """Raise FileNotFoundError when EC2_CONFIG is missing."""
    logger.EC2_CONFIG = 'notreal.xml'

    with pytest.raises(FileNotFoundError):
        logger._enable_ec2_config_event_log()


@pytest.mark.skipif(not logger.EC2_CONFIG_DEPS,
                    reason="EC2Config requirements not met.")
@pytest.mark.skipif(sys.version_info < (3,),
                    reason="Not supported in this Python version.")
def test_configure_ec2_config_event_log_raises_filenotfound(mocker):
    """Raise FileNotFoundError when EC2_CONFIG_EVENT_LOG is missing."""
    logger.EC2_CONFIG_EVENT_LOG = 'notreal.xml'

    with pytest.raises(FileNotFoundError):
        logger._configure_ec2_config_event_log()


@pytest.mark.skipif(not logger.EC2_CONFIG_DEPS,
                    reason="EC2Config requirements not met.")
def test_enable_ec2_config_event_log(mocker):
    """Enable EC2Config Event Logging."""
    data = '''<?xml version="1.0" standalone="yes"?>
    <Ec2ConfigurationSettings>
        <Plugins>
            <Plugin>
                <Name>Ec2EventLog</Name>
                <State>Disabled</State>
            </Plugin>
        </Plugins>
    </Ec2ConfigurationSettings>
    '''

    mo_ = mocker.mock_open(read_data=data)
    mocker.patch('io.open', mo_, create=True)

    logger._enable_ec2_config_event_log()

    # Verify we opened the file twice, once for read and once for write
    assert mo_.call_args_list == [
        mocker.call(logger.EC2_CONFIG),
        mocker.call(logger.EC2_CONFIG, mode='wb')
    ]

    # Convert write calls to xml tree
    handle = mo_()
    result = xml.etree.ElementTree.ElementTree(
        xml.etree.ElementTree.fromstring(
            _pytest_stringify_write_calls(handle.write.call_args_list)))

    # Assert that the Ec2EventLog plugin is enabled
    ec2eventlog_plugin_present = False
    plugins = result.getroot().find('Plugins').findall('Plugin')
    for plugin in plugins:
        if plugin.find('Name').text == 'Ec2EventLog':
            ec2eventlog_plugin_present = True
            assert plugin.find('State').text == 'Enabled'
            break

    # Assert that the Ec2EventLog plugin is present
    assert ec2eventlog_plugin_present


@pytest.mark.skipif(not logger.EC2_CONFIG_DEPS,
                    reason="EC2Config requirements not met.")
def test_configure_ec2config_write_all_events(mocker):
    """Configure EC2Config Event Logging with all events."""
    data = '''<?xml version="1.0" standalone="yes"?>
    <EventLogConfig>
    </EventLogConfig>
    '''

    mo_ = mocker.mock_open(read_data=data)
    mocker.patch('io.open', mo_, create=True)

    logger._configure_ec2_config_event_log()

    # Verify we opened the file twice, once for read and once for write
    assert mo_.call_args_list == [
        mocker.call(logger.EC2_CONFIG_EVENT_LOG),
        mocker.call(logger.EC2_CONFIG_EVENT_LOG, mode='wb')
    ]

    # Convert write calls to xml tree
    handle = mo_()
    result = xml.etree.ElementTree.ElementTree(
        xml.etree.ElementTree.fromstring(
            _pytest_stringify_write_calls(handle.write.call_args_list)))

    # Get all the present events
    events = result.getroot().findall('Event')
    events_present = set()
    for event in events:
        if (
            event.find('ErrorType').text in logger.MESSAGE_TYPES and
            event.find('Category').text == 'Application' and
            event.find('AppName').text == 'Watchmaker'
        ):
            events_present.add(event.find('ErrorType').text)

    # Validate that all expected events were written
    events_missing = events_present.symmetric_difference(logger.MESSAGE_TYPES)
    assert not events_missing


@pytest.mark.skipif(not logger.EC2_CONFIG_DEPS,
                    reason="EC2Config requirements not met.")
def test_configure_ec2config_skip_if_events_present(mocker):
    """Check that EC2Config Event Log config skips pre-existing events."""
    data = '''<?xml version="1.0" standalone="yes"?>
    <EventLogConfig>
        <Event>
            <Category>Application</Category>
            <ErrorType>Error</ErrorType>
            <NumEntries>999999</NumEntries>
            <LastMessageTime>2008-09-10T00:00:00.000Z</LastMessageTime>
            <AppName>Watchmaker</AppName>
        </Event>
        <Event>
            <Category>Application</Category>
            <ErrorType>Information</ErrorType>
            <NumEntries>999999</NumEntries>
            <LastMessageTime>2008-09-10T00:00:00.000Z</LastMessageTime>
            <AppName>Watchmaker</AppName>
        </Event>
        <Event>
            <Category>Application</Category>
            <ErrorType>Warning</ErrorType>
            <NumEntries>999999</NumEntries>
            <LastMessageTime>2008-09-10T00:00:00.000Z</LastMessageTime>
            <AppName>Watchmaker</AppName>
        </Event>
    </EventLogConfig>
    '''

    mo_ = mocker.mock_open(read_data=data)
    mocker.patch('io.open', mo_, create=True)

    logger._configure_ec2_config_event_log()

    # Verify we read the data
    assert mo_.call_args_list == [
        mocker.call(logger.EC2_CONFIG_EVENT_LOG),
    ]

    # Verify we didn't write anything
    handle = mo_()
    assert handle.write.call_count == 0


###
# EC2Launch Tests
###
@pytest.mark.skipif(not logger.EC2_LAUNCH_DEPS,
                    reason="EC2Launch requirements not met.")
@pytest.mark.skipif(sys.version_info < (3,),
                    reason="Not supported in this Python version.")
def test_configure_ec2_launch_event_log_raises_filenotfound(mocker):
    """Raise FileNotFoundError when EC2_LAUNCH_LOG_CONFIG is missing."""
    logger.EC2_LAUNCH_LOG_CONFIG = 'notreal.json'

    with pytest.raises(FileNotFoundError):
        logger._configure_ec2_launch_event_log()


@pytest.mark.skipif(not logger.EC2_LAUNCH_DEPS,
                    reason="EC2Launch requirements not met.")
def test_schedule_ec2launch_event_logging_raises_calledproccesserror(mocker):
    """Raise FileNotFoundError when EC2_LAUNCH_SEND_EVENTS is missing."""
    logger.EC2_LAUNCH_SEND_EVENTS = 'notreal.ps1'

    with pytest.raises(subprocess.CalledProcessError):
        logger._schedule_ec2_launch_event_log()


def test_configure_ec2launch_write_all_events(mocker):
    """Configure EC2Launch Event Logging with all events."""
    # Start with an empty data set, so all events should be written
    data = '{}'

    mo_ = mocker.mock_open(read_data=data)
    mocker.patch('io.open', mo_, create=True)

    logger._configure_ec2_launch_event_log()

    # Verify we opened the file twice, once for read and once for write
    assert mo_.call_args_list == [
        mocker.call(logger.EC2_LAUNCH_LOG_CONFIG),
        mocker.call(logger.EC2_LAUNCH_LOG_CONFIG, mode='w')
    ]

    # Convert write calls to json
    handle = mo_()
    result = json.loads(
        _pytest_stringify_write_calls(handle.write.call_args_list))

    expected_events = []
    for msg_type in logger.MESSAGE_TYPES:
        expected_events += [{
            'logName': 'Application',
            'source': 'Watchmaker',
            'level': msg_type,
            'numEntries': '999'
        }]

    # Validate that all expected events were written
    assert 'events' in result
    for event in expected_events:
        assert event in result['events']


def test_configure_ec2launch_skip_if_events_present(mocker):
    """Check that EC2Launch Event Log config skips pre-existing events."""
    # Load all event types into the data
    events = []
    for msg_type in logger.MESSAGE_TYPES:
        events += [{
            'logName': 'Application',
            'source': 'Watchmaker',
            'level': msg_type,
            'numEntries': '999'
        }]
    data = json.dumps({'events': events})

    mo_ = mocker.mock_open(read_data=data)
    mocker.patch('io.open', mo_, create=True)

    logger._configure_ec2_launch_event_log()

    # Verify we read the data
    assert mo_.call_args_list == [
        mocker.call(logger.EC2_LAUNCH_LOG_CONFIG),
    ]

    # Verify we didn't write anything
    handle = mo_()
    assert handle.write.call_count == 0
