# -*- coding: utf-8 -*-
"""IMDS module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging

from watchmaker.utils.conditions import HAS_AZURE, HAS_BOTO3
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider

log = logging.getLogger(__name__)


def tag_resource(targets, status):

    if not targets:
        return

    if AWSProvider().identifier == targets[0]["target_type"].lower():
        tag_aws_resource(targets, status)

    if AzureProvider().identifier == targets[0]["target_type"].lower():
        tag_azure_resource(targets, status)


def tag_aws_resource(targets, status):
    for target in targets:
        log.debug("Tagging AWS Resource")
        if HAS_BOTO3:
            # Do tagging
            log.debug("Tag Resource")
            pass


def tag_azure_resource(targets, status):
    for target in targets:
        log.debug("Tagging Azure Resource")
        if HAS_AZURE:
            # Do tagging
            log.debug("Tag Resource")
            pass
