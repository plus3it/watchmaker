"""Conditions module."""

HAS_BOTO3 = False
try:
    import boto3  # noqa: F401

    HAS_BOTO3 = True
except ImportError:
    pass

HAS_AZURE = False
try:
    from azure.core import pipeline  # noqa: F401
    from azure.identity import (  # noqa: F401
        AzureCliCredential,
        _credentials,
    )
    from azure.mgmt.resource import (  # noqa: F401
        ResourceManagementClient,
        resources,
    )

    HAS_AZURE = True
except ImportError:
    pass
