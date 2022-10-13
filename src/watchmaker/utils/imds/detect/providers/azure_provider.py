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

from six.moves import urllib

from watchmaker.utils.imds.detect.providers.provider import AbstractProvider


class AzureProvider(AbstractProvider):
    """
        Concrete implementation of the Azure cloud provider.
    """
    identifier = 'azure'

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata_url = (
            'http://169.254.169.254/metadata/instance?api-version=2017-12-01'
        )
        self.vendor_file = '/sys/class/dmi/id/sys_vendor'
        self.headers = {'Metadata': 'true'}

    def identify(self):
        """
            Tries to identify Azure using all the implemented options
        """
        self.logger.info('Try to identify DO')
        return self.check_vendor_file() or self.check_metadata_server()

    def check_metadata_server(self):
        """
            Tries to identify Azure via metadata server
        """
        self.logger.debug('Checking Azure metadata')
        try:
            return self.__is_valid_server()
        except BaseException as e:
            self.logger.error(e)
            return False

    def check_vendor_file(self):
        """
            Tries to identify Azure provider by reading the /sys/class/dmi/id/sys_vendor
        """
        self.logger.debug('Checking Azure vendor file')
        if exists(self.vendor_file):
            with open(self.vendor_file) as f:
                if "Microsoft Corporation" in f.read():
                    return True
        return False

    def __is_valid_server(self):
        with urllib.request.urlopen(self.metadata_url, timeout = AbstractProvider.url_timeout, headers=self.headers) as response:
                return response.status == 200