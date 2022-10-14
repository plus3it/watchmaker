# -*- coding: utf-8 -*-
"""Watchmaker Config module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import collections
import logging
import os

import yaml
from compatibleversion import check_version

import watchmaker.utils.imds.detect
from watchmaker.utils.imds.detect.providers.provider import AbstractProvider
from watchmaker import static
from watchmaker.exceptions import WatchmakerError
from watchmaker.utils import urllib

log = logging.getLogger(__name__)


def get_watchmaker_configs(system, worker_args, config_path=None):
    """
    Read and validate configuration data for installation.

    Returns:
        :obj:`collections.OrderedDict`: Returns the data from the the YAML
        configuration file, scoped to the value of ``system`` and
        merged with the value of the ``"All"`` key.

    """
    if not config_path:
        log.warning("User did not supply a config. Using the default config.")
        config_path = os.path.join(static.__path__[0], "config.yaml")
    else:
        log.info("User supplied config being used.")

    # Convert a local config path to a URI
    config_path = watchmaker.utils.uri_from_filepath(config_path)

    # Get the raw config data
    data = ""
    try:
        data = watchmaker.utils.urlopen_retry(config_path).read()
    except (ValueError, urllib.error.URLError):
        msg = (
            'Could not read config file from the provided value "{0}"! '
            "Check that the config is available.".format(config_path)
        )
        log.critical(msg)
        raise

    config_full = yaml.safe_load(data)
    try:
        config_all = config_full.get("all", [])
        config_system = config_full.get(system, [])
        config_status = config_full.get("status", [])
        config_version_specifier = config_full.get("watchmaker_version", None)
    except AttributeError:
        msg = "Malformed config file. Must be a dictionary."
        log.critical(msg)
        raise

    # If both config and config_system are empty, raise
    if not config_system and not config_all:
        msg = "Malformed config file. No workers for this system."
        log.critical(msg)
        raise WatchmakerError(msg)

    if config_version_specifier and not check_version(
        watchmaker.__version__, config_version_specifier
    ):
        msg = (
            "Watchmaker version {} is not compatible with the config "
            "file (watchmaker_version = {})"
        ).format(watchmaker.__version__, config_version_specifier)
        log.critical(msg)
        raise WatchmakerError(msg)

    # Merge the config data, preserving the listed order of workers.
    # The worker order from config_system has precedence over config_all.
    # This is managed by adding config_system to the config first, using
    # the loop order, e.g. config_system + config_all. In the loop, if the
    # worker is already in the config, it is always the worker from
    # config_system.
    # To also preserve precedence of worker options from config_system, the
    # worker_config from config_all is updated with the config from
    # config_system, then the config is replaced with the worker_config.
    config = collections.OrderedDict()
    for worker in config_system + config_all:
        try:
            # worker is a single-key dict, where the key is the name of the
            # worker and the value is the worker parameters. we need to
            # test if the worker is already in the config, but a dict is
            # is not hashable so cannot be tested directly with
            # `if worker not in config`. this bit of ugliness extracts the
            # key and its value so we can use them directly.
            worker_name, worker_config = list(worker.items())[0]
            if worker_name not in config:
                # Add worker to config
                config[worker_name] = {"config": worker_config}
                log.debug("%s config: %s", worker_name, worker_config)
            else:
                # Worker is present in both config_system and config_all,
                # config[worker_name]['config'] is from config_system,
                # worker_config is from config_all
                worker_config.update(config[worker_name]["config"])
                config[worker_name]["config"] = worker_config
                log.debug("%s extra config: %s", worker_name, worker_config)
                # Need to (re)merge cli worker args so they override
                config[worker_name]["__merged"] = False
            if not config[worker_name].get("__merged"):
                # Merge worker_args into config params
                config[worker_name]["config"].update(worker_args)
                config[worker_name]["__merged"] = True
        except Exception:
            msg = "Failed to merge worker config; worker={0}".format(worker)
            log.critical(msg)
            raise

    log.debug(
        "Command-line arguments merged into worker configs: %s", worker_args
    )

    config_status = get_status_target_by_target_type(config_status)

    return config, config_status


def get_status_target_by_target_type(config_status):
    if config_status:
        target_type = get_target_type()

        if target_type != AbstractProvider.identifier:
            targets = [
                target
                for target in config_status["targets"]
                if target["target_type"].lower() == target_type
            ]

            if targets:
                return {"targets": targets}

    return None


def get_tag_targets(status_config, status_type):
    if status_config:
        status_type = status_type.lower()
        targets = [
            target
            for target in status_config["targets"]
            if target["status_type"].lower() == status_type
        ]

        return targets


def has_required_tag(config_status, target_type, status_type):
    """Checks if tag is required and riases exception if found"""
    targets = [target for target in config_status["targets"]
               if target["required"] and
               target["target_type"].lower() == target_type and
               target["status_type"].lower() == status_type]

    if targets:
        target_types = set()
        for target in targets:
            target_types.append(
                "{0} : {1}".format(target["target_type"],
                                   target["status_type"])
            )
        raise Exception(
            "Target types and tags {0} are required but \
             unable to tag the environment".format(
                target_types
            )
        )

    return False


def get_target_type():
    return watchmaker.utils.imds.detect.provider()
