# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

# Supports Python2 and Python3 test mocks
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from watchmaker.config.status import (
    get_supported_cloud_identifiers_with_prereqs,
)


@patch(
    "watchmaker.config.status.get_cloud_ids_with_prereqs",
    return_value=["aws", "azure"],
)
def test_get_provider_identifiers(prereqs):
    """Test status config allowed provider_types."""
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

    ids = get_supported_cloud_identifiers_with_prereqs(config_status)

    assert ids is not None
    assert "aws" in ids
    assert "azure" in ids
    assert "gcp" not in ids
    assert "none" not in ids
