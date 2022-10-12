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
import urllib.request
from pathlib import Path

from watchmaker.utils.imds.detect.providers.provider import AbstractProvider


class AWSProvider(AbstractProvider):
    """Concrete implementation of the AWS cloud provider."""


    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.vendor_file = "/sys/class/dmi/id/product_version"


    def identify(self):
        """
        Tries to identify AWS using all the implemented options
        """
        self.logger.info("Try to identify AWS")
        response = self.check_metadata_server() or self.check_vendor_file()


    def check_metadata_server(self):
        """
        Tries to identify AWS via metadata server
        """
        self.logger.debug("Checking AWS metadata")
        try:
            with urllib.request.urlopen(self.metadata_url) as response:
                data = response.read()

            response = json.loads(data.decode("utf-8"))

            if response["imageId"].startswith("ami-",) and response[
                "instanceId"
            ].startswith("i-"):
                return True
            return False
        except BaseException as e:
            self.logger.error(e)
            return False
