# -*- coding: utf-8 -*-
"""Exposes urllib imports with additional request handlers."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

# pylint: disable=import-error
from six.moves.urllib import error, parse, request  # noqa: F401

from watchmaker.utils.urllib.request_handlers import HAS_BOTO3, S3Handler

if HAS_BOTO3:
    request.install_opener(request.build_opener(S3Handler))
