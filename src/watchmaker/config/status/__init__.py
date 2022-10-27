# -*- coding: utf-8 -*-
"""Status Config module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging

STATUS = {
    "RUNNING": "Running",
    "COMPLETE": "Completed",
    "ERROR": "Error",
}


def is_valid_status_config(config):
    """Validate config."""
    is_valid = True
    if config and "targets" in config:
        for target in config["targets"]:
            if "key" not in target or not target["key"]:
                is_valid = False
                logging.error("Status target is missing key or value")
            if "target_type" not in target or not target["target_type"]:
                is_valid = False
                logging.error("Status target is missing target_type or value")
            if "required" in target:
                if not isinstance(target["required"], bool):
                    is_valid = False
                    logging.error("Status target required value is not a bool")

    return is_valid


def get_status(status_key):
    """Get formatted status message for status key provided."""
    status = STATUS.get(status_key, None)
    return status if status else status_key


def get_target_key(target):
    """Get key from the target."""
    return target["key"]


def is_target_required(target):
    """Get whether target required."""
    return target["required"]


def get_targets_by_target_type(config_status, target_type):
    """Get the targets for the target type."""
    if config_status and target_type:
        target_type = target_type.lower()
        if target_type:
            return [
                target
                for target in config_status["targets"]
                if target["target_type"].lower() == target_type
            ]

    return None
