# -*- coding: utf-8 -*-
"""Status Module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

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

        status_provider_ids = []
        # get supported providers with prereqs
        supported_providers = status_config.get_sup_cloud_ids_w_prereqs(config)

        if supported_providers:
            # Detect Provider
            cloud_identifier = provider(supported_providers)
            if cloud_identifier != AbstractStatusProvider.identifier:
                status_provider_ids.append(cloud_identifier)

        if not status_provider_ids:
            # Supported provider doesn't exist or not detected
            # Check for supported providers missing prereqs
            get_missing_prereq_cloud_identifiers = (
                status_config.get_req_cloud_ids_wo_prereqs(config)
            )

            if get_missing_prereq_cloud_identifiers:
                # Detect provider
                cloud_identifier = provider(
                    get_missing_prereq_cloud_identifiers
                )

                if cloud_identifier != AbstractStatusProvider.identifier:
                    # We found a provider without prereqs
                    # error out since it is required
                    raise StatusProviderError(
                        "Missing prereqs for required provider %s"
                        % cloud_identifier
                    )

        status_provider_ids += status_config.get_non_cloud_identifiers(config)

        self.status_providers = self.__get_status_providers(
            status_provider_ids
        )

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
