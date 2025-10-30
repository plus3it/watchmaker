"""Azure Status Provider."""

import json
import logging

import watchmaker.utils as utils
from watchmaker.conditions import HAS_AZURE
from watchmaker.exceptions import StatusProviderError
from watchmaker.status.providers.abstract import AbstractStatusProvider


class AzureStatusProvider(AbstractStatusProvider):
    """Concrete implementation of the Azure status cloud provider."""

    identifier = "azure"

    def __init__(self, provider, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_id_url = (
            "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
        )
        self.initial_status = False
        self.subscription_id = None
        self.resource_id = None
        self.provider = provider
        self.initialize()

    def initialize(self):
        """Initialize subscription and resource id."""
        if self.subscription_id and self.resource_id:
            return

        try:
            self.__set_ids_from_server()
        except Exception:
            self.logger.exception("Error retrieving ids from metadata service")

    def update_status(self, key, status, required):
        """Tag an Azure instance with the key and status provided."""
        self.logger.debug("Tagging Azure Resource")
        if HAS_AZURE and self.subscription_id and self.resource_id and status:
            try:
                self.__tag_azure_resouce(key, status)
            except Exception:
                logging.exception("Exception while tagging azure resource")
            else:
                return
        self.__error_on_required_status(required)

    def __tag_azure_resouce(self, key, status):
        self.logger.debug("Tag Resource %s with  %s:%s", self.resource_id, key, status)
        credential = AzureCliCredential()  # noqa: F821

        resource_client = ResourceManagementClient(  # noqa: F821
            credential,
            self.subscription_id,
        )

        body = {
            "operation": self.__get_operation(),
            "properties": {"tags": {key: status}},
        }
        resource_client.tags.create_or_update_at_scope(self.resource_id, body)
        self.logger.debug("Resource tag created")

    def __set_ids_from_server(self):
        """Retrieve Azure instance id from metadata."""
        response = utils.urlopen_retry(self.metadata_id_url, self.DEFAULT_TIMEOUT)
        data = json.load(response)
        self.subscription_id = data["compute"]["subscriptionId"]
        self.resource_id = data["compute"]["resourceId"]

    def __get_operation(self):
        """
        Get the tag operation.

        Return "create" if initial status otherwise "udpate"
        """
        if self.initial_status:
            self.initial_status = False
            return "create"

        return "update"

    def __error_on_required_status(self, required):
        """Error if tag is required."""
        if required:
            err_prefix = "Watchmaker status tag required for azure resources,"
            if not HAS_AZURE:
                err_msg = "required python sdk was not found"
            elif not self.resource_id or not self.subscription_id:
                err_msg = "resource and subcription ids \
                        were not found via metadata service"
            else:
                err_msg = "watchmaker was unable to update status"

            err_msg = f"{err_prefix} {err_msg}"
            logging.error(err_msg)
            raise StatusProviderError(err_msg)
