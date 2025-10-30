"""AWS Status Provider."""

import logging

import watchmaker.utils as utils
from watchmaker.conditions import HAS_BOTO3

if HAS_BOTO3:
    import boto3  # type: ignore

from watchmaker.exceptions import StatusProviderError
from watchmaker.status.providers.abstract import AbstractStatusProvider


class AWSStatusProvider(AbstractStatusProvider):
    """Concrete implementation of the AWS status cloud provider."""

    identifier = "aws"

    def __init__(self, provider, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_id_url = "http://169.254.169.254/latest/meta-data/instance-id"
        self.metadata_region_url = (
            "http://169.254.169.254/latest/meta-data/placement/region"
        )

        self.instance_id = None
        self.region = None
        self.provider = provider
        self.initialize()

    def initialize(self):
        """Initialize instance id."""
        if self.instance_id and self.region:
            return
        try:
            self.logger.debug("Initialize AWS instance_id and region")
            self.instance_id = self.__get_response_from_server(self.metadata_id_url)
            self.region = self.__get_response_from_server(self.metadata_region_url)
        except Exception:
            self.logger.exception("Error retrieving id/region from metadata service")

    def update_status(self, key, status, required):
        """Tag an AWS EC2 instance with the key and status provided."""
        self.logger.debug("Tagging AWS Resource if HAS_BOTO3")
        self.logger.debug(
            "HAS_BOTO3=%s instance_id=%s status=%s",
            HAS_BOTO3,
            self.instance_id,
            status,
        )
        if HAS_BOTO3 and self.instance_id and status:
            try:
                self.__tag_aws_instance(key, status)
            except Exception:
                logging.exception("Exception while tagging aws instance")
            else:
                return
        self.__error_on_required_status(required)

    def __tag_aws_instance(self, key, status):
        """Create or update instance tag with provided status."""
        self.logger.debug("Tag Instance %s with  %s:%s", self.instance_id, key, status)

        try:
            client = boto3.client("ec2", self.region)
            response = client.create_tags(
                Resources=[
                    self.instance_id,
                ],
                Tags=[
                    {"Key": key, "Value": status},
                ],
            )
        except Exception:
            self.logger.exception("Error tagging AWS instance")
            raise

        self.logger.debug("Create tag response %s", response)

    def __get_response_from_server(self, metadata_url):
        """Get response for provided metadata_url."""
        headers = self.provider.get_metadata_request_headers()
        request = utils.urllib_utils.request.Request(
            metadata_url,
            data=None,
            headers=headers,
        )
        response = utils.urlopen_retry(
            request,
            self.DEFAULT_TIMEOUT,
        )
        return response.read().decode("utf-8")

    def __error_on_required_status(self, required):
        """Error if tag is required."""
        if required:
            err_prefix = "Watchmaker status tag required for aws resources,"
            if not HAS_BOTO3:
                err_msg = "required boto3 python sdk was not found"
            elif not self.instance_id:
                err_msg = "instance id was not found via metadata service"
            else:
                err_msg = "watchmaker was unable to update status"

            err_msg = f"{err_prefix} {err_msg}"
            logging.error(err_msg)
            raise StatusProviderError(err_msg)
