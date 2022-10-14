# -*- coding: utf-8 -*-
"""AWS Provider."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import json
import logging
from os.path import exists

from six.moves import urllib

from watchmaker.utils.imds.detect.providers.provider import AbstractProvider


class AWSProvider(AbstractProvider):
    """Concrete implementation of the AWS cloud provider."""

    identifier = "aws"

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_url = (
            "http://169.254.169.254/latest/dynamic/instance-identity/document"
        )
        self.vendor_files = (
            "/sys/class/dmi/id/product_version",
            "/sys/class/dmi/id/bios_vendor",
        )

    def identify(self):
        """
        Tries to identify AWS using all the implemented options
        """
        self.logger.info("Try to identify AWS")
        return self.check_metadata_server() or self.check_vendor_file()

    def check_metadata_server(self):
        """
        Tries to identify AWS via metadata server
        """
        self.logger.debug("Checking AWS metadata")
        try:
            data = self.__get_data_from_server()

            response = json.loads(data.decode("utf-8"))

            if response["imageId"].startswith("ami-",) and response[
                "instanceId"
            ].startswith("i-"):
                return True
            return False
        except BaseException as e:
            self.logger.error(e)
            return False

    def check_vendor_file(self):
        """
        Tries to identify AWS provider by reading the
        /sys/class/dmi/id/product_version
        """
        self.logger.debug("Checking AWS vendor file")
        for vendor_file in self.vendor_files:
            if exists(vendor_file):
                with open(vendor_file) as f:
                    if "amazon" in f.read().lower():
                        return True
        return False

    def __get_data_from_server(self):
        with urllib.request.urlopen(self.metadata_url,
                                    timeout=AbstractProvider.url_timeout) \
                as response:
            return response.read()
