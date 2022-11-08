# -*- coding: utf-8 -*-
"""Status Config module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging

SUPPORTED_CLOUD_PROVIDERS = ["aws", "azure"]
SUPPORTED_NON_CLOUD_PROVIDERS = []

STATUS = {
    "RUNNING": "Running",
    "COMPLETE": "Completed",
    "ERROR": "Error",
}


def is_valid(config):
    """Validate config."""
    if not config:
        return True

    targets = config.get("targets", None)
    if not targets:
        return False

    valid = True
    for target in targets:
        if "key" not in target or not target["key"]:
            valid = False
            logging.error("Status target is missing key or value")
        if "target_type" not in target or not target["target_type"]:
            valid = False
            logging.error("Status target is missing target_type or value")
        if not isinstance(target.get("required"), bool):
            valid = False
            logging.error("Status target required value is not a bool")

    return valid


def get_status(status_key):
    """Get status message.

    returns string: formatted status message from key provided
                   or status_key as status
    """
    status = STATUS.get(status_key, None)
    return status if status else status_key


def get_target_key(target):
    """Get key from the target."""
    return target["key"]


def is_target_required(target):
    """Get whether target required."""
    return target["required"]


def get_target_type(target):
    """Get target type."""
    return target["target_type"]


def get_targets_by_target_types(config_status, target_type):
    """Get the targets for the target types."""
    return [
        target
        for target in config_status.get("targets", [])
        if target["target_type"].lower() == target_type
    ]


def get_cloud_identifiers(config_status):
    """Get unique list of cloud targets."""
    return list(set(
        target.get("target_type").lower()
        for target in config_status.get("targets", [])
        if target.get("target_type", "").lower() in SUPPORTED_CLOUD_PROVIDERS
    ))


def get_non_cloud_identifiers(config_status):
    """Get unique list of other provider targets."""
    return list(set(
        target.get("target_type").lower()
        for target in config_status.get("targets", [])
        if target.get(
            "target_type", "").lower() in SUPPORTED_NON_CLOUD_PROVIDERS
    ))
