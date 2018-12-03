# -*- coding: utf-8 -*-
"""PyTest configuration."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)


def pytest_configure(config):
    """Set system to recognize that its in a test environment."""
    import sys
    sys._called_from_test = True


def pytest_unconfigure(config):
    """Unset test environment."""
    import sys
    del sys._called_from_test
