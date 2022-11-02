# -*- coding: utf-8 -*-
"""AWS Provider."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging
from os.path import exists

import watchmaker.utils as utils
from watchmaker.utils.imds.detect.providers.provider import AbstractProvider


class AzureProvider(AbstractProvider):
    """Concrete implementation of the Azure cloud provider."""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_url = (
            'http://169.254.169.254/metadata/instance?api-version=2021-02-01'
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

        # Convert a local vendor file to a URI
        if exists(self.vendor_file):
            vendor_file_path = utils.uri_from_filepath(self.vendor_file)
            try:
                check_vendor_file = utils.urlopen_retry(vendor_file_path)
                if "Microsoft Corporation" in check_vendor_file.read():
                    return True
            except (ValueError, utils.urllib.error.URLError):
                pass
        return False

    def __is_valid_server(self):
        """Retrieve Azure metadata."""
        response = utils.urlopen_retry(self.metadata_url)
        return response.status == 200