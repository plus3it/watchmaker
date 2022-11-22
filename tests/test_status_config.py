# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from watchmaker.config.status import get_cloud_identifiers


def test_get_provider_identifiers():
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

    ids = get_cloud_identifiers(config_status)

    assert ids is not None
    assert "aws" in ids
    assert "azure" in ids
    assert "gcp" not in ids
    assert "none" not in ids
