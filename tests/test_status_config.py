# -*- coding: utf-8 -*-
"""Providers main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from watchmaker.config.status import get_supported_cloud_target_identifiers


def test_get_target_identifiers():

    config_status = \
        {
            "targets": [
                {
                    "key": 'WatchmakerStatus',
                    "required": False,
                    "target_type": 'aws',
                },
                {
                    "key": 'WatchmakerStatus',
                    "required": False,
                    "target_type": 'azure',
                },
                {
                    "key": 'WatchmakerStatus',
                    "required": False,
                    "target_type": 'gcp',
                }
            ]
        }

    ids = get_supported_cloud_target_identifiers(config_status)

    assert ids is not None
    assert "aws" in ids
    assert "azure" in ids
    assert "gcp" not in ids
    assert "none" not in ids
