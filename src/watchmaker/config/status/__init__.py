# -*- coding: utf-8 -*-
"""Status Config module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import logging

from watchmaker.conditions import HAS_AZURE, HAS_BOTO3

SUPPORTED_CLOUD_PROVIDERS = [
    {"provider": "aws", "has_prereq": HAS_BOTO3},
    {"provider": "azure", "has_prereq": HAS_AZURE},
]
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
    return provider.get("required", False)


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


def get_sup_cloud_ids_w_prereqs(config_status):
    """Get supported cloud providers with prereqs and in config."""
    supported = get_cloud_ids_with_prereqs()
    return list(
        set(
            provider.get("provider_type").lower()
            for provider in config_status.get("providers", [])
            if provider.get("provider_type", "").lower() in supported
        )
    )


def get_req_cloud_ids_wo_prereqs(config_status):
    """Get supported cloud providers without prereqs and in config."""
    missing_prereqs = get_cloud_ids_missing_prereqs()
    return list(
        set(
            provider.get("provider_type").lower()
            for provider in config_status.get("providers", [])
            if provider.get("provider_type", "").lower() in missing_prereqs
            and provider.get("required", False)
        )
    )


def get_cloud_ids_with_prereqs():
    """Get supported cloud providers with prereqs."""
    providers = set()

    for cloud_provider in SUPPORTED_CLOUD_PROVIDERS:
        if cloud_provider["has_prereq"]:
            logging.debug(
                "Adding %s to list of providers with prereqs",
                cloud_provider["provider"],
            )
            providers.add(cloud_provider["provider"])
        else:
            logging.debug(
                "Skipping provider %s prereqs not found",
                cloud_provider["provider"],
            )

    return list(providers)


def get_cloud_ids_missing_prereqs():
    """Get supported cloud providers without prereqs."""
    providers = set()

    for cloud_provider in SUPPORTED_CLOUD_PROVIDERS:
        if not cloud_provider["has_prereq"]:
            providers.add(cloud_provider["provider"])

    return list(providers)


def get_non_cloud_identifiers(config_status):
    """Get unique list of other provider providers."""
    providers = set()
    for provider in SUPPORTED_NON_CLOUD_PROVIDERS:
        providers.add(provider["provider"])

    non_cloud_provider_list = list(providers)

    return list(
        set(
            provider.get("provider_type").lower()
            for provider in config_status.get("providers", [])
            if provider.get("provider_type", "").lower()
            in non_cloud_provider_list
        )
    )
