# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,protected-access
"""Salt worker main test module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import shutil
import stat
import time

import oschmod

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


def test_set_path_perms():
    """Check file permissions are correctly set."""
    # create dirs
    topdir = 'testdir1'
    testdir = os.path.join(topdir, 'testdir2', 'testdir3')
    os.makedirs(testdir)

    # create files
    fileh = open(os.path.join(topdir, 'file1'), "w+")
    fileh.write("contents")
    fileh.close()

    fileh = open(os.path.join(testdir, 'file2'), "w+")
    fileh.write("contents")
    fileh.close()

    # set permissions to badness
    triple7 = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP\
        | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH\
        | stat.S_IXOTH
    oschmod.set_mode(topdir, triple7)
    oschmod.set_mode(testdir, triple7)
    oschmod.set_mode(os.path.join(topdir, 'file1'), triple7)
    oschmod.set_mode(os.path.join(testdir, 'file2'), triple7)
    time.sleep(2)  # modes aren't always ready to go immediately

    # set permissions - the test
    watchmaker.utils.set_path_perms(topdir)
    time.sleep(2)  # modes aren't always ready to go immediately

    # check it out
    assert oct(oschmod.get_mode(topdir))[-3:] == "700"
    assert oct(
        oschmod.get_mode(os.path.join(topdir, 'testdir2')))[-3:] == "700"
    assert oct(oschmod.get_mode(testdir))[-3:] == "700"
    assert oct(oschmod.get_mode(os.path.join(topdir, 'file1')))[-3:] == "600"
    assert oct(oschmod.get_mode(os.path.join(testdir, 'file2')))[-3:] == "600"

    # clean up
    shutil.rmtree(topdir)
