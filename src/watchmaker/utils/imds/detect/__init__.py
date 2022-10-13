# -*- coding: utf-8 -*-
"""Detect  module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import logging


from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider

log = logging.getLogger(__name__)

def provider(excluded=[]):
    if "aws" not in excluded:
        result = AWSProvider().identify();
        if result:
            log.debug("IMDS detected result is aws")
            return AWSProvider().identifier

    if "azure" not in excluded:
        result = AzureProvider().identify();
        if result:
            log.debug("IMDS detected result is azure")
            return AzureProvider().identifier

    log.debug("IMDS detected result is unknown")
    return "unknown"
