"""PyTest configuration."""

import sys


def pytest_configure(config):
    """Set system to recognize that its in a test environment."""
    sys._called_from_test = True


def pytest_unconfigure(config):
    """Unset test environment."""
    del sys._called_from_test
