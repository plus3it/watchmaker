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

    providers = config.get("providers", None)
    if not providers:
        return False

    valid = True
    for provider in providers:
        if "key" not in provider or not provider["key"]:
            valid = False
            logging.error("Status provider is missing key or value")
        if "provider_type" not in provider or not provider["provider_type"]:
            valid = False
            logging.error("Status provider is missing provider_type or value")
        if not isinstance(provider.get("required"), bool):
            valid = False
            logging.error("Status provider required value is not a bool")

    return valid


def get_status(status_key):
    """Get status message.

    returns string: formatted status message from key provided
                   or status_key as status
    """
    status = STATUS.get(status_key, None)
    return status if status else status_key


def get_provider_key(provider):
    """Get key from the provider."""
    return provider["key"]


def is_provider_required(provider):
    """Get whether provider required."""
    return provider["required"]


def get_provider_type(provider):
    """Get provider type."""
    return provider["provider_type"]


def get_providers_by_provider_types(config_status, provider_type):
    """Get the providers for the provider types."""
    return [
        provider
        for provider in config_status.get("providers", [])
        if provider["provider_type"].lower() == provider_type
    ]


def get_cloud_identifiers(config_status):
    """Get unique list of cloud providers."""
    return list(
        set(
            provider.get("provider_type").lower()
            for provider in config_status.get("providers", [])
            if provider.get("provider_type", "").lower()
            in SUPPORTED_CLOUD_PROVIDERS
        )
    )


def get_non_cloud_identifiers(config_status):
    """Get unique list of other provider providers."""
    return list(
        set(
            provider.get("provider_type").lower()
            for provider in config_status.get("providers", [])
            if provider.get("provider_type", "").lower()
            in SUPPORTED_NON_CLOUD_PROVIDERS
        )
    )
