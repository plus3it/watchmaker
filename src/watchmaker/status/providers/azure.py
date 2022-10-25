# -*- coding: utf-8 -*-
"""Azure Status Provider."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import json
import logging

import watchmaker.utils as utils
from watchmaker.status.providers.abstract import (AbstractStatusProvider,
                                                  StatusProviderException)
from watchmaker.utils.conditions import HAS_AZURE


class AzureStatusProvider(AbstractStatusProvider):
    """Concrete implementation of the Azure status cloud provider."""
    identifier = 'azure'

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_id_url = \
            "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
        self.initial_status = False
        self.subscription_id = None
        self.resource_id = None
        self.initialize()

    def initialize(self):
        """Initializes subscription and resource ids"""
        if not self.subscription_id or not self.resource_id:
            try:
                self.__set_ids_from_server()
            except BaseException as ex:
                self.logger.error(
                    "Error retrieving ids from metadata service %s", ex)

    def tag_resource(self, status_type, key, status, required):
        """Tags an Azure instance with the key and status provided."""
        self.logger.debug("Tagging Azure Resource")
        if HAS_AZURE and \
            self.subscription_id and \
                self.resource_id and \
                status:
            try:
                self.__tag_azure_resouce(key, status)
                return
            except BaseException as ex:
                logging.error("Exception while tagging azure resource %s", ex)
        self.__error_on_required_status(status_type, required)

    def __tag_azure_resouce(self, key, status):
        self.logger.debug("Tag Resource %s with  %s:%s",
                          self.instance_id, key, status)
        # pylint: disable=attribute-defined-outside-init
        # pylint: disable=undefined-variable
        credential = AzureCliCredential()  # type: ignore # noqa F821

        # pylint: disable=attribute-defined-outside-init
        # pylint: disable=undefined-variable
        resource_client =  \
            ResourceManagementClient(credential, self.get_subscription_id())  # type: ignore # noqa F821

        body = {
            "operation": self.__get_operation(),
            "properties": {
                "tags": {key: status}
            }
        }
        resource_client.tags.create_or_update_at_scope(
            self.get_resource_id(), body)
        self.logger.debug("Resource tag created")

    def __set_ids_from_server(self):
        """Retrieves Azure instance id from metadata."""
        response = utils.urlopen_retry(self.metadata_url)
        data = json.load(response)
        self.subscription_id = data["compute"]["subscriptionId"]
        self.resource_id = data["compute"]["resourceId"]

    def __get_operation(self):
        """Gets the tag operation

        Return "create" if initial status otherwise "udpate"
        """
        if self.initial_status:
            self.initial_status = False
            return "create"

        return "update"

    def __error_on_required_status(self, status_type, required):
        if required:
            err_prefix = "Tag Status is required for azure resource \
                    and status type %s but ", status_type
            if not HAS_AZURE:
                err_msg = \
                    "%s required python sdk was not found", err_prefix
            else:
                err_msg = \
                    "%s resource and subcription ids \
                        were not found via metadata service", err_prefix
            logging.error(err_msg)
            raise StatusProviderException(err_msg)
