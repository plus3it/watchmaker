# -*- coding: utf-8 -*-
"""Status Module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging

import watchmaker.config.status as status_config
from watchmaker.status.providers.aws import AWSStatusProvider
from watchmaker.status.providers.azure import AzureStatusProvider
from watchmaker.utils.imds.detect import provider


class Status():
    """Status factory for providers."""

    def __init__(self, config=None, excluded=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.status_provider = None
        self.identifier = None
        self.targets = None
        self.initialize(config, excluded)

    def initialize(self, config=None, excluded=None):
        """Initialize and get provider."""
        if not self.identifier or not self.status_provider:
            self.identifier = provider(excluded)
            self.status_provider = \
                self.__get_status_provider_by_id()

        if not self.targets and config:
            self.targets = \
                status_config.get_targets_by_target_type(
                    config, self.identifier)

    def get_status_provider_identifier(self):
        """Get provider identifier."""
        return self.identifier

    def get_status_provider(self):
        """Get provider."""
        return self.status_provider

    def tag_resource(self, status_type, status):
        """Tag resource with key and status provided."""
        if not self.status_provider or not self.targets:
            return

        targets = \
            status_config.get_targets_by_status_type(self.targets, status_type)

        for target in targets:
            key = status_config.get_target_key(target)
            required = status_config.is_target_required(target)
            self.status_provider.tag_resource(
                status_type, key,
                status_config.get_status(status_type, status), required)

    def __get_status_provider_by_id(self):
        """Get provider by identifier."""
        if self.identifier == AWSStatusProvider().identifier:
            return AWSStatusProvider()
        if self.identifier == AzureStatusProvider().identifier:
            return AzureStatusProvider()
        return None
