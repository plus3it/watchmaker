# -*- coding: utf-8 -*-
"""Status Module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging

import watchmaker.config.status as status_config
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
        self.targets = {}
        self.initialize(config)

    def initialize(self, config=None):
        """Initialize status providers."""
        if not config:
            return

        status_provider_ids = []
        if status_config.get_cloud_identifiers(config):
            cloud_identifier = provider()
            if cloud_identifier != AbstractStatusProvider.identifier:
                status_provider_ids.append(cloud_identifier)

        status_provider_ids += status_config.get_non_cloud_identifiers(config)

        self.status_providers = self.__get_status_providers(
            status_provider_ids
        )

        for identifier in self.status_providers:
            self.targets[
                identifier
            ] = status_config.get_targets_by_target_types(config, identifier)

    def update_status(self, status):
        """Update status for each status provider."""
        if not self.status_providers or not self.targets:
            return

        logging.debug(self.targets)

        for identifier, targets in self.targets.items():
            status_provider = self.status_providers.get(identifier)
            for target in targets:
                status_provider.update_status(
                    status_config.get_target_key(target),
                    status_config.get_status(status),
                    status_config.is_target_required(target),
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
