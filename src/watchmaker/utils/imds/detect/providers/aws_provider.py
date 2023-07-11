# -*- coding: utf-8 -*-
"""AWS Provider."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import json
import logging
from os.path import exists

import watchmaker.utils as utils
from watchmaker.utils.imds.detect.providers.provider import AbstractProvider


class AWSProvider(AbstractProvider):
    """Concrete implementation of the AWS cloud provider."""

    identifier = "aws"
    imds_token = None

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_url = (
            "http://169.254.169.254/latest/dynamic/instance-identity/document"
        )

        self.metadata_imds_v2_token_url = (
            "http://169.254.169.254/latest/api/token"
        )

        self.vendor_files = (
            "/sys/class/dmi/id/product_version",
            "/sys/class/dmi/id/bios_vendor",
        )

    def identify(self):
        """Identify AWS using all the implemented options."""
        self.logger.info("Try to identify AWS")
        return self.check_metadata_server() or self.check_vendor_file()

    def check_metadata_server(self):
        """Identify AWS via metadata server."""
        self.logger.debug("Checking AWS metadata")
        try:
            self.__request_token()
            return self.__is_valid_server()
        except BaseException as ex:
            self.logger.error(ex)
            return False

    def check_vendor_file(self):
        """Identify whether this is an AWS provider.

        Checks the vendor files to see if it contains amazon.
        """
        self.logger.debug("Checking AWS vendor file")
        for vendor_file in self.vendor_files:
            data = self.__get_file_contents(vendor_file)
            if bool(data and "amazon" in data.lower()):
                return True
        return False

    def __is_valid_server(self):
        """Determine if valid metadata server."""
        """Retrieve AWS metadata."""
        data = self.__call_urlopen_retry(
            self.metadata_url,
            self.DEFAULT_TIMEOUT,
            headers=self.__get_metadata_request_headers(),
        )

        if data:
            response = json.loads(data)
            if response["imageId"].startswith(
                "ami-",
            ) and response[
                "instanceId"
            ].startswith("i-"):
                return True
        return False

    def __get_metadata_request_headers(self):
        if AWSProvider.imds_token:
            self.logger.debug("Making IMDSv2 Call")
            return {"X-aws-ec2-metadata-token": AWSProvider.imds_token}

        self.logger.debug("Making IMDSv1 Call")
        return None

    def __request_token(self):
        try:
            self.logger.debug("Create request for token")
            AWSProvider.imds_token = self.__call_urlopen_retry(
                self.metadata_imds_v2_token_url,
                self.DEFAULT_TIMEOUT,
                headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
                method="PUT",
            )
        except BaseException as error:
            self.logger.debug("Error is %s", error)

    def __get_file_contents(self, file):
        """Get file contents if exists."""
        if not exists(file):
            return None
        # Convert a local vendor file to a URI
        file_path = utils.uri_from_filepath(file)
        try:
            return self.__call_urlopen_retry(file_path, self.DEFAULT_TIMEOUT)
        except (ValueError, utils.urllib.error.URLError):
            return None

    def __call_urlopen_retry(self, uri, timeout, headers=None, method=None):
        result = utils.urlopen_retry(
            uri, timeout, optional_headers=headers, method=method
        )
        if result.status == 200:
            return result.read().decode("utf-8")
        return None
