# -*- coding: utf-8 -*-
"""Status Module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging

import watchmaker.utils.imds.detect.providers.provider as provider
from watchmaker.status.providers.aws_status_provider import AWSStatusProvider
from watchmaker.status.providers.azure_status_provider import \
    AzureStatusProvider
import watchmaker.config.status as status_config


class Status():

    def __init__(self, config=None, excluded=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.status_provider = None
        self.identifier = None
        self.targets = None
        self.initialize(config, excluded)

    def initialize(self, config=None, excluded=None):
        """Initializes Status if not already done"""
        if not self.identifier or not self.status_provider:
            self.identifier = provider(excluded)
            self.status_provider = \
                self.__get_status_provider_by_id(self.identifier)

        if self.identifier and config:
            self.targets = \
                status_config.get_targets_by_target_type(self.identifier)

    def get_status_provider_identifier(self):
        return self.identifier

    def get_status_provider(self):
        return self.status_provider

    def tag_resource(self, status_type):
        """Update Tag resources key and status provided."""
        if not self.status_provider or not self.targets:
            return

        targets = \
            status_config.get_targets_by_status_type(self.targets, status_type)

        for target in targets:
            key = status_config.get_target_key(target)
            required = status_config.is_target_required(target)
            self.status_provider.tag_resource(
                status_type, key,
                status_config.get_status(status_type), required)

    def __get_status_provider_by_id(id, logger=None):
        """Get provider for this resource"""
        if id == AWSStatusProvider().identifier:
            return AWSStatusProvider(logger)
        if id == AzureStatusProvider().identifier:
            return AzureStatusProvider(logger)
        return None
