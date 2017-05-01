# -*- coding: utf-8 -*-
"""Watchmaker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import pytest

import watchmaker


@pytest.fixture
def setup_object():
    """Test setup."""
    pass


def test_main():
    """Placeholder for tests."""
    assert watchmaker.__version__ == watchmaker.__version__
