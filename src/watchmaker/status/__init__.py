# -*- coding: utf-8 -*-
"""Status Module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import logging

import watchmaker.config.status as status_config
from watchmaker.exceptions import StatusProviderError
from watchmaker.status.providers.abstract import AbstractStatusProvider
from watchmaker.status.providers.aws import AWSStatusProvider
from watchmaker.status.providers.azure import AzureStatusProvider
from watchmaker.utils.imds.detect import provider


class Status:
    """Status factory for providers."""

    _PROVIDERS = {
        AWSStatusProvider.identifier: AWSStatusProvider,
        AzureStatusProvider.identifier: AzureStatusProvider,
    }

    def __init__(self, config=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.status_providers = {}
        self.providers = {}
        self.initialize(config)

    def initialize(self, config=None):
        """Initialize status providers."""
        if not config:
            return

        detected_providers = self.__get_detected_provider_ids(config)

        self.status_providers = self.__get_status_providers(detected_providers)

        for identifier in self.status_providers:
            self.providers[
                identifier
            ] = status_config.get_providers_by_provider_types(
                config, identifier
            )

    def update_status(self, status):
        """Update status for each status provider."""
        if not self.status_providers or not self.providers:
            return

        for identifier, providers in self.providers.items():
            status_provider = self.status_providers.get(identifier)
            for provider_type in providers:
                status_provider.update_status(
                    status_config.get_provider_key(provider_type),
                    status_config.get_status(status),
                    status_config.is_provider_required(provider_type),
                )

    def get_detected_providers(self):
        """Get detected providers."""
        return list(self.status_providers)

    def __get_status_providers(self, identifiers):
        """Get providers by identifiers."""
        status_providers = {}
        for identifier in identifiers:
            status_providers[identifier] = Status._PROVIDERS.get(identifier)()

        return status_providers

    def __get_detected_provider_ids(self, config):
        """Get detected status provider ids."""
        detected_providers = []

        identifier = self.__detect_provider_with_prereqs(config)

        if identifier:
            self.logger.debug("Detected provider %s", identifier)
            detected_providers.append(identifier)
        else:
            self.__error_on_required_provider(config)

        detected_providers.extend(
            status_config.get_non_cloud_identifiers(config)
        )

        return detected_providers

    def __detect_provider_with_prereqs(self, config):
        """Detect supported providers with prereqs."""
        supported_providers = status_config.get_sup_cloud_ids_w_prereqs(config)
        # Detect providers in config that have prereqs
        identifier = provider(supported_providers)
        return (
            None
            if identifier == AbstractStatusProvider.identifier
            else identifier
        )

    def __error_on_required_provider(self, config):
        """Detect required providers in config that do no have prereqs."""
        req_providers_missing_prereqs = (
            status_config.get_req_cloud_ids_wo_prereqs(config)
        )
        self.logger.debug(
            "For each required provider missing "
            "prereqs, attempt to detect provider: %s",
            req_providers_missing_prereqs,
        )
        cloud_identifier = provider(req_providers_missing_prereqs)

        # If a req provider is found raise StatusProviderError
        if cloud_identifier != AbstractStatusProvider.identifier:
            raise StatusProviderError(
                "Required Provider detected that is missing prereqs: %s"
                % cloud_identifier
            )
