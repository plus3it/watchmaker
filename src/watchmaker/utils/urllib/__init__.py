# -*- coding: utf-8 -*-
"""Exposes urllib imports with additional request handlers."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

# pylint: disable=import-error
from six.moves.urllib import error, parse, request  # type:ignore # noqa F401

from watchmaker.conditions import HAS_BOTO3

if HAS_BOTO3:
    from watchmaker.utils.urllib.request_handlers import S3Handler
    request.install_opener(request.build_opener(S3Handler))
