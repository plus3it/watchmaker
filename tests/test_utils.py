# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,protected-access
"""Salt worker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import watchmaker.utils

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch('os.path.exists', autospec=True)
@patch('shutil.rmtree', autospec=True)
@patch('shutil.copytree', autospec=True)
def test_copytree_no_force(mock_copy, mock_rm, mock_exists):
    """Test that copytree results in correct calls without force option."""
    random_src = 'aba51e65-afd2-5020-8117-195f75e64258'
    random_dst = 'f74d03de-7c1d-596f-83f3-73748f2e238f'

    watchmaker.utils.copytree(random_src, random_dst)
    mock_copy.assert_called_with(random_src, random_dst)
    assert mock_rm.call_count == 0
    assert mock_exists.call_count == 0

    watchmaker.utils.copytree(random_src, random_dst, force=False)
    mock_copy.assert_called_with(random_src, random_dst)
    assert mock_rm.call_count == 0
    assert mock_exists.call_count == 0


@patch('os.path.exists', autospec=True)
@patch('shutil.rmtree', autospec=True)
@patch('shutil.copytree', autospec=True)
def test_copytree_force(mock_copy, mock_rm, mock_exists):
    """Test that copytree results in correct calls with force option."""
    random_src = '44b6df59-db6f-57cb-a570-ccd55d782561'
    random_dst = '72fe7962-a7af-5f2f-899b-54798bc5e79f'

    watchmaker.utils.copytree(random_src, random_dst, force=True)
    mock_copy.assert_called_with(random_src, random_dst)
    mock_rm.assert_called_with(random_dst)
    mock_exists.assert_called_with(random_dst)


def test_clean_none():
    """Check string 'None' conversion to None."""
    assert not watchmaker.utils.clean_none('None')
    assert not watchmaker.utils.clean_none('none')
    assert not watchmaker.utils.clean_none(None)
    assert watchmaker.utils.clean_none('not none') == 'not none'


@patch('os.path.exists', autospec=True)
@patch('watchmaker.utils.copytree', autospec=True)
@patch("os.walk", autospec=True)
def test_copy_subdirectories(mock_os, mock_copy, mock_exists):
    """Test that copy_subdirectories executes expected calls."""
    random_src = '580a9176-20f6-4f64-b77a-75dbea14d74f'
    random_dst = '6538965c-5131-414a-897f-b01f7dfb6c2b'
    mock_exists.return_value = False
    mock_os.return_value = [
        ('580a9176-20f6-4f64-b77a-75dbea14d74f', ('87a2a74d',)),
        ('580a9176-20f6-4f64-b77a-75dbea14d74f/87a2a74d', (),
            ('6274fd83', '1923c65a')),
    ].__iter__()

    watchmaker.utils.copy_subdirectories(random_src, random_dst, None)
    assert mock_copy.call_count == 1
