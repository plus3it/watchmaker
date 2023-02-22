# -*- coding: utf-8 -*-
"""Detect  module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import concurrent.futures
import logging

from watchmaker.exceptions import CloudDetectError, InvalidProviderError
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider
from watchmaker.utils.imds.detect.providers.provider import AbstractProvider

log = logging.getLogger(__name__)

MAX_WORKERS = 10

CLOUD_PROVIDERS = {"aws": AWSProvider, "azure": AzureProvider}


def provider(supported_providers=None):
    """Identify and return identifier."""
    exception_list = []
    results = []
    futures = []
    supported_providers = supported_providers if supported_providers else []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:
        for cloud_identifier in supported_providers:
            if CLOUD_PROVIDERS.get(cloud_identifier, None):
                futures.append(
                    executor.submit(
                        identify, CLOUD_PROVIDERS[cloud_identifier]
                    )
                )

    concurrent.futures.wait(futures)
    for fut in futures:
        try:
            results.append(fut.result())
        except InvalidProviderError:
            pass
        except BaseException as ex:
            exception_list.append(str(ex))

    if len(results) > 1:
        raise CloudDetectError("Detected more than one cloud provider")

    if len(results) == 0:
        return AbstractProvider.identifier

    return results[0]


def identify(cloud_provider):
    """Identify provider."""
    if cloud_provider().identify():
        return cloud_provider.identifier

    raise InvalidProviderError(
        "Environment is not %s" % cloud_provider.identifier
    )
