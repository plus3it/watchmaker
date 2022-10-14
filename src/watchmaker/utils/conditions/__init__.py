HAS_BOTO3 = False
try:
    import boto3  # noqa: F401

    HAS_BOTO3 = True
except ImportError:
    pass

HAS_AZURE = False
try:
    from azure.mgmt.resource import ResourceManagementClient  # noqa: F401

    HAS_AZURE = True
except ImportError:
    pass
