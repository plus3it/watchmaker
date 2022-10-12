# -*- coding: utf-8 -*-
"""Detect  module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import logging


from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider


def provider(excluded=[]):
    if "aws" not in excluded and AWSProvider().identify():
        logging.debug("IMDS detected result is aws")
        return "aws"
    else:
        logging.debug("IMDS detected result is unknown")
        return "unknown"
