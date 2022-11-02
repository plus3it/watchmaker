# -*- coding: utf-8 -*-
"""AWS Status Provider."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging

import watchmaker.utils as utils
from watchmaker.conditions import HAS_BOTO3
from watchmaker.exceptions import StatusProviderError
from watchmaker.status.providers.abstract import AbstractStatusProvider


class AWSStatusProvider(AbstractStatusProvider):
    """Concrete implementation of the AWS status cloud provider."""

    identifier = 'aws'

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_id_url = (
            'http://169.254.169.254/latest/meta-data/instance-id'
        )
        self.instance_id = None
        self.initialize()

    def initialize(self):
        """Initialize instance id."""
        if self.instance_id:
            return
        try:
            self.__set_id_from_server()
        except BaseException as ex:
            self.logger.error(
                "Error retrieving id from metadata service %s", ex)

    def tag_resource(self, key, status, required):
        """Tag an AWS EC2 instance with the key and status provided."""
        self.logger.debug("Tagging AWS Resource")
        if HAS_BOTO3 and self.instance_id and status:
            try:
                self.__tag_aws_instance(key, status)
                return
            except BaseException as ex:
                logging.error("Exception while tagging aws instance %s", ex)
        self.__error_on_required_status(required)

    def __tag_aws_instance(self, key, status):
        """Create or update instance tag with provided status."""
        self.logger.debug("Tag Instance %s with  %s:%s",
                          self.instance_id, key, status)
        # pylint: disable=attribute-defined-outside-init
        # pylint: disable=undefined-variable
        client = boto3.client('ec2')  # type: ignore # noqa F821
        client.create_tags(
            Resources=[
                self.instance_id,
            ],
            Tags=[
                {
                    'Key': key,
                    'Value': status
                },
            ]
        )

    def __set_id_from_server(self):
        """Retrieve AWS instance id from metadata."""
        response = utils.urlopen_retry(self.metadata_id_url)
        self.instance_id = response.read()

    def __error_on_required_status(self, required):
        """Error if tag is required."""
        if required:
            err_prefix = "Watchmaker status tag required for aws resources, "
            if not HAS_BOTO3:
                err_msg = \
                    "%s required python sdk was not found", err_prefix
            else:
                err_msg = \
                    "%s instance id \
                        was not found via metadata service", err_prefix
            logging.error(err_msg)
            raise StatusProviderError(err_msg)
