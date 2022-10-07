HAS_BOTO3 = False
try:
    import boto3

    HAS_BOTO3 = True
except ImportError:
    pass

HAS_AZURE = False
try:
    from azure.mgmt.resource import ResourceManagementClient

    HAS_AZURE = True
except ImportError:
    pass
