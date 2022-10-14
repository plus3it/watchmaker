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
    """Tag resources key and status provided."""
    if not targets:
        return

    if AWSProvider().identifier == targets[0]["target_type"].lower():
        tag_aws_resource(targets, status)

    if AzureProvider().identifier == targets[0]["target_type"].lower():
        tag_azure_resource(targets, status, "create")


def update_tag_resource(targets, status):
    """Update Tag resources key and status provided."""
    if not targets:
        return

    if AWSProvider().identifier == targets[0]["target_type"].lower():
        tag_aws_resource(targets, status)

    if AzureProvider().identifier == targets[0]["target_type"].lower():
        tag_azure_resource(targets, status, "update")


def tag_aws_resource(targets, status):
    """Tag an AWS EC2 instance with the key and status provided."""
    for target in targets:
        log.debug("Tagging AWS Resource")
        if HAS_BOTO3:
            # Do tagging
            log.debug("Tag Resource")
            # pylint: disable=undefined-variable
            client = boto3.client('ec2')  # noqa F821
            client.create_tags(
                DryRun=True,
                Resources=[
                    AWSProvider().get_instance_id(),
                ],
                Tags=[
                    {
                        'Key': target["key"],
                        'Value': status
                    },
                ]
            )
            pass


def tag_azure_resource(targets, status, operation):
    """Tag an Azure instance with the key and status provided."""
    for target in targets:
        log.debug("Tagging Azure Resource")
        if HAS_AZURE:
            # Do tagging
            log.debug("Tag Resource %s", target["key"])
            log.debug("With status %s", status)
            # pylint: disable=undefined-variable
            credential = AzureCliCredential() # noqa F821
            subscription_id = AzureProvider.subscription_id
            resource_group = AzureProvider.resource_group
            # pylint: disable=undefined-variable
            resource_client =  \
            ResourceManagementClient(credential, subscription_id)   # noqa F821
            resource_list = resource_client.resources.list_by_resource_group(
                resource_group)
            tag_dict = {target["key"]: status}
            for resource in resource_list:
                body = {
                    "operation": operation,
                    "properties": {
                        "tags": tag_dict
                    }
                }
                resource_client.tags.create_or_update_at_scope(
                    resource.id, body)
            log.debug("Resource tag created")
            pass
