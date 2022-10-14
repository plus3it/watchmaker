# -*- coding: utf-8 -*-
"""Detect  module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging

from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider
from watchmaker.utils.imds.detect.providers.provider import AbstractProvider

log = logging.getLogger(__name__)


def provider(excluded=None):
    """Identify and return identifier."""
    if not is_excluded(AWSProvider().identifier, excluded):
        result = AWSProvider().identify()
        if result:
            log.debug("IMDS detected result is aws")
            return AWSProvider().identifier

    if not is_excluded(AzureProvider().identifier, excluded):
        result = AzureProvider().identify()
        if result:
            log.debug("IMDS detected result is azure")
            return AzureProvider().identifier

    log.debug("IMDS detected result is unknown")
    return AbstractProvider.identifier


def is_excluded(identifier, excluded=None):
    """Check if identifier is in excluded list."""
    if not excluded:
        return False
    return identifier in excluded
