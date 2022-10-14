# -*- coding: utf-8 -*-
"""AWS Provider."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging
# pylint: disable=redefined-builtin
from io import open
from os.path import exists

from six.moves import urllib

from watchmaker.utils.imds.detect.providers.provider import AbstractProvider


class AzureProvider(AbstractProvider):
    """Concrete implementation of the Azure cloud provider."""

    identifier = 'azure'
    subscription_id = None
    resource_group = None

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_url = (
            'http://169.254.169.254/metadata/instance?api-version=2017-12-01'
        )
        self.vendor_file = '/sys/class/dmi/id/sys_vendor'
        self.headers = {'Metadata': 'true'}

    def identify(self):
        """Identify Azure using all the implemented options."""
        self.logger.info('Try to identify DO')
        return self.check_vendor_file() or self.check_metadata_server()

    def check_metadata_server(self):
        """Identify Azure via metadata server."""
        self.logger.debug('Checking Azure metadata')
        try:
            return self.__is_valid_server()
        except BaseException as ex:
            self.logger.error(ex)
            return False

    def check_vendor_file(self):
        """Identify whether this in an Azure provider.

        Read file /sys/class/dmi/id/sys_vendor
        """
        self.logger.debug('Checking Azure vendor file')
        if exists(self.vendor_file):
            with open(self.vendor_file, encoding="utf-8") as vendor_file:
                if "Microsoft Corporation" in vendor_file.read():
                    return True
        return False

    def __is_valid_server(self):
        """Retrieve Azure metadata."""
        with urllib.request.urlopen(self.metadata_url,
                                    timeout=AbstractProvider.url_timeout) \
                as response:
            return response.status == 200

    @staticmethod
    def reset():
        """Reset static vars."""
        AzureProvider.subscription_id = None
        AzureProvider.resource_group = None
