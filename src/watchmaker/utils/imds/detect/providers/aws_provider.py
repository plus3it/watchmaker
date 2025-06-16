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
import os

import watchmaker.utils as utils
from watchmaker.utils.imds.detect.providers.provider import AbstractProvider

IMDS_TOKEN_TIMEOUT = int(os.getenv("IMDS_TOKEN_TIMEOUT", "7200"))


class AWSProvider(AbstractProvider):
    """Concrete implementation of the AWS cloud provider."""

    identifier = "aws"

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_url = (
            "http://169.254.169.254/latest/dynamic/instance-identity/document"
        )

        self.metadata_imds_v2_token_url = "http://169.254.169.254/latest/api/token"

        self.imds_token = self.__request_token()

    def identify(self):
        """Identify AWS using all the implemented options."""
        self.logger.info("Try to identify AWS")
        return self.check_metadata_server()

    def check_metadata_server(self):
        """Identify AWS via metadata server."""
        self.logger.debug("Checking AWS metadata")
        try:
            return self.__is_valid_server()
        except Exception as ex:  # pylint: disable=broad-exception-caught
            self.logger.error(ex)
            return False

    def get_metadata_request_headers(self):
        """Return metadata request header if imds token is set."""
        if self.imds_token:
            self.logger.debug("Returning AWS IMDSv2 Token Header")
            return {"X-aws-ec2-metadata-token": self.imds_token}

        self.logger.debug("AWS IMDSv2 Token not found")
        return None

    def __is_valid_server(self):
        """Determine if valid metadata server."""
        data = self.__call_urlopen_retry(
            self.metadata_url,
            self.DEFAULT_TIMEOUT,
            headers=self.get_metadata_request_headers(),
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

    def __request_token(self):
        try:
            self.logger.debug("Create request for token")
            return self.__call_urlopen_retry(
                self.metadata_imds_v2_token_url,
                self.DEFAULT_TIMEOUT,
                headers={"X-aws-ec2-metadata-token-ttl-seconds": IMDS_TOKEN_TIMEOUT},
                method="PUT",
            )
        except Exception as error:  # pylint: disable=broad-exception-caught
            self.logger.debug("Failed to set IMDSv2 token: %s", error)
        return None

    def __call_urlopen_retry(self, uri, timeout, headers=None, method=None):
        request_uri = utils.urllib_utils.request.Request(
            uri,
            data=None,
            headers=headers,
            method=method,
        )

        result = utils.urlopen_retry(request_uri, timeout)
        if result.status == 200:
            return result.read().decode("utf-8")
        return None
