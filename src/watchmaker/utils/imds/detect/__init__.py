# -*- coding: utf-8 -*-
"""Detect  module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import concurrent.futures
import logging

from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider
from watchmaker.utils.imds.detect.providers.provider import AbstractProvider

log = logging.getLogger(__name__)

MAX_WORKERS = 10


def provider():
    """Identify and return identifier."""
    exception_list = []
    results = []
    futures = []
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_WORKERS) as executor:
        futures.append(executor.submit(identify, AWSProvider))
        futures.append(executor.submit(identify, AzureProvider))

    concurrent.futures.wait(futures)
    for fut in futures:
        try:
            result = fut.result()
            if result != AbstractProvider.identifier:
                results.append(result)
        except BaseException as ex:
            exception_list.append(str(ex))

    if len(results) > 1:
        raise Exception("Detected more than one cloud provider")

    if len(results) == 0:
        return AbstractProvider.identifier

    return results[0]


def identify(cloud_provider):
    """Identify provider."""
    result = cloud_provider().identify()
    if result:
        log.debug("IMDS detected result is %s", result)
        return result

    return AbstractProvider.identifier
