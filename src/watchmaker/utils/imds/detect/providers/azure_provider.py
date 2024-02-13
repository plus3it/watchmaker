# -*- coding: utf-8 -*-
"""Azure Provider."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import logging

import watchmaker.utils as utils
from watchmaker.utils.imds.detect.providers.provider import AbstractProvider


class AzureProvider(AbstractProvider):
    """Concrete implementation of the Azure cloud provider."""

    identifier = "azure"

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_url = (
            "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
        )
        self.headers = {"Metadata": "true"}

    def identify(self):
        """Identify Azure using all the implemented options."""
        self.logger.info("Try to identify Azure")
        return self.check_metadata_server()

    def check_metadata_server(self):
        """Identify Azure via metadata server."""
        self.logger.debug("Checking Azure metadata")
        try:
            return self.__is_valid_server()
        except Exception as ex:  # pylint: disable=broad-exception-caught
            self.logger.warning("Error while checking server %s", str(ex))
            return False

    def __is_valid_server(self):
        """Retrieve Azure metadata."""
        response = utils.urlopen_retry(self.metadata_url, self.DEFAULT_TIMEOUT)
        return response.status == 200
