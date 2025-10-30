"""Providers main test module."""

from watchmaker.exceptions import CloudProviderDetectionError

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from unittest.mock import patch

from watchmaker.status import Status
from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider
from watchmaker.utils.imds.detect.providers.azure_provider import AzureProvider


@patch.object(AWSProvider, "identify", return_value=True)
@patch.object(AzureProvider, "identify", return_value=False)
@patch(
    "watchmaker.config.status.get_cloud_with_prereqs",
    return_value=["aws", "azure"],
)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_status(
    aws_provider_mock,
    azure_provider_mock,
    supported_identifiers_mock,
    request_token_mock,
):
    """Test provider is AWS."""
    config = {
        "status": {
            "providers": [
                {"key": "WatchmakerStatus", "required": False, "provider_type": "aws"},
                {
                    "key": "WatchmakerStatus",
                    "required": False,
                    "provider_type": "azure",
                },
            ],
        },
    }
    config_status = config.get("status")
    status = Status(config_status)
    detected_providers = status.get_detected_status_providers()
    assert len(detected_providers) == 1
    assert detected_providers.get("aws").identifier == AWSProvider.identifier


@patch.object(AWSProvider, "identify", return_value=False)
@patch.object(AzureProvider, "identify", return_value=True)
@patch(
    "watchmaker.config.status.get_cloud_with_prereqs",
    return_value=[],
)
@patch(
    "watchmaker.config.status.get_cloud_missing_prereqs",
    return_value=["aws", "azure"],
)
@patch.object(
    AWSProvider,
    "_AWSProvider__request_token",
    return_value=(None),
)
def test_req_status_provider(
    aws_provider_mock,
    azure_provider_mock,
    supported_identifiers_mock,
    missing_prereqs_mock,
    request_token_mock,
):
    """Test provider is AWS."""
    config = {
        "status": {
            "providers": [
                {"key": "WatchmakerStatus", "required": False, "provider_type": "aws"},
                {"key": "WatchmakerStatus", "required": True, "provider_type": "azure"},
            ],
        },
    }
    config_status = config.get("status")

    try:
        Status(config_status)
    except CloudProviderDetectionError as spe:
        assert str(spe) == "Required Provider detected that is missing prereqs: azure"
