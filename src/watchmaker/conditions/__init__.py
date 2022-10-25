# -*- coding: utf-8 -*-
"""Conditions module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

HAS_BOTO3 = False
try:
    import boto3  # type: ignore # noqa: F401

    HAS_BOTO3 = True
except ImportError:
    pass

HAS_AZURE = False
try:
    from azure.core import pipeline  # type: ignore # noqa: F401
    from azure.identity import AzureCliCredential, _credentials  # type: ignore # noqa: F401 E501
    from azure.mgmt.resource import ResourceManagementClient  # type: ignore # noqa: F401 E501
    from azure.mgmt.resource import resources  # type: ignore # noqa: F401
    HAS_AZURE = True
except ImportError:
    pass
