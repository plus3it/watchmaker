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
    instance_id = None

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_url = (
            "http://169.254.169.254/latest/dynamic/instance-identity/document"
        )
        self.metadata_id_url = (
            'http://169.254.169.254/latest/meta-data/instance-id'
        )
        self.vendor_files = (
            "/sys/class/dmi/id/product_version",
            "/sys/class/dmi/id/bios_vendor",
        )

    def identify(self):
        """Identify AWS using all the implemented options."""
        self.logger.info("Try to identify AWS")
        return self.check_metadata_server() or self.check_vendor_file()

    def get_instance_id(self):
        """Get AWS instance id."""
        if self.instance_id:
            return self.instance_id
        return self.__get_instance_id_from_server()

    def check_metadata_server(self):
        """Identify AWS via metadata server."""
        self.logger.debug("Checking AWS metadata")
        try:
            data = self.__get_data_from_server()

            response = json.loads(data.decode("utf-8"))

            if response["imageId"].startswith("ami-",) and response[
                "instanceId"
            ].startswith("i-"):
                AWSProvider.instance_id = response["instanceId"]
                return True
            return False
        except BaseException as e:
            self.logger.error(e)
            return False

    def check_vendor_file(self):
        """Identifiy whether this is an AWS provider.

        Reads file/sys/class/dmi/id/product_version
        """
        self.logger.debug("Checking AWS vendor file")
        for vendor_file in self.vendor_files:
            if exists(vendor_file):
                with open(vendor_file) as f:
                    if "amazon" in f.read().lower():
                        return True
        return False

    def __get_data_from_server(self):
        """Retrieve AWS metadata."""
        with urllib.request.urlopen(self.metadata_url,
                                    timeout=AbstractProvider.url_timeout) \
                as response:
            return response.read()

    def __get_instance_id_from_server(self):
        """Retrieve AWS instance id from metadata."""
        try:
            with urllib.request.urlopen(self.metadata_id_url,
                                        timeout=AbstractProvider.url_timeout) \
                    as response:
                AWSProvider.instance_id = response.read()
                return AWSProvider.instance_id
        except BaseException as e:
            self.logger.error("Exception getting instance id {0}".format(e))
            return None

    @staticmethod
    def reset():
        """Reset static vars."""
        AWSProvider.instance_id = None
