# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.config.status import (
    get_cloud_with_prereqs,
    get_non_cloud_providers,
    get_required_cloud_wo_prereqs,
    get_supported_cloud_w_prereqs,
)


@patch(
    "watchmaker.config.status.get_cloud_with_prereqs",
    return_value=["aws", "azure"],
)
def test_supported_cloud_w_prereqs(prereqs):
    """Test get required ids that are have prereqs."""
    config_status = {
        "providers": [
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "aws",
            },
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "azure",
            },
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "gcp",
            },
        ]
    }

    ids = get_supported_cloud_w_prereqs(config_status)

    assert ids is not None
    assert "aws" in ids
    assert "azure" in ids
    assert "gcp" not in ids
    assert "none" not in ids


@patch(
    "watchmaker.config.status.get_cloud_missing_prereqs",
    return_value=["aws", "azure"],
)
def test_req_cloud_wo_prereqs(prereqs):
    """Test get required ids that are missing prereqs."""
    config_status = {
        "providers": [
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "aws",
            },
            {
                "key": "WatchmakerStatus",
                "required": True,
                "provider_type": "azure",
            },
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "gcp",
            },
        ]
    }

    ids = get_required_cloud_wo_prereqs(config_status)

    assert ids is not None
    assert "aws" not in ids
    assert "azure" in ids
    assert "gcp" not in ids
    assert "none" not in ids


@patch(
    "watchmaker.config.status.get_cloud_missing_prereqs",
    return_value=[],
)
def test_no_req_cloud_wo_prereqs(prereqs):
    """Test get required ids that are missing prereqs."""
    config_status = {
        "providers": [
            {
                "key": "WatchmakerStatus",
                "required": True,
                "provider_type": "aws",
            },
            {
                "key": "WatchmakerStatus",
                "required": True,
                "provider_type": "azure",
            },
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "gcp",
            },
        ]
    }

    assert not get_required_cloud_wo_prereqs(config_status)


@patch(
    "watchmaker.config.status.SUPPORTED_CLOUD_PROVIDERS",
    [
        {"provider": "aws", "has_prereq": True},
        {"provider": "azure", "has_prereq": False},
    ],
)
def test_get_cloud_with_prereqs():
    """Test get ids with prereqs."""
    providers = get_cloud_with_prereqs()

    assert len(providers) == 1
    assert "aws" == providers[0]


@patch(
    "watchmaker.config.status.SUPPORTED_CLOUD_PROVIDERS",
    [
        {"provider": "aws", "has_prereq": True},
        {"provider": "azure", "has_prereq": False},
    ],
)
def test_cloud_ids_missing_prereqs():
    """Test get ids missing prereqs."""
    providers = get_cloud_with_prereqs()

    assert len(providers) == 1
    assert "azure" != providers[0]


@patch(
    "watchmaker.config.status.SUPPORTED_NON_CLOUD_PROVIDERS",
    [
        {"provider": "file"},
        {"provider": "db"},
    ],
)
def test_get_non_cloud_providers():
    """Test get non cloud identifiers matching config."""
    config_status = {
        "providers": [
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "sqs",
            },
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "file",
            },
        ]
    }

    providers = get_non_cloud_providers(config_status)

    assert len(providers) == 1
    assert "file" == providers[0]


@patch(
    "watchmaker.config.status.SUPPORTED_NON_CLOUD_PROVIDERS",
    [],
)
def test_no_non_cloud_providers():
    """Test empty SUPPORTED_NON_CLOUD_PROVIDERS."""
    config_status = {
        "providers": [
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "sqs",
            },
            {
                "key": "WatchmakerStatus",
                "required": False,
                "provider_type": "file",
            },
        ]
    }

    assert not get_non_cloud_providers(config_status)
