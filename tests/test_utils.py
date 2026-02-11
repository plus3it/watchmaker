"""Salt worker main test module."""

import platform
from pathlib import Path
from unittest.mock import patch

import pytest

import watchmaker.utils


@patch("pathlib.Path.exists", autospec=True)
@patch("shutil.rmtree", autospec=True)
@patch("shutil.copytree", autospec=True)
def test_copytree_no_force(mock_copy, mock_rm, mock_exists):
    """Test that copytree results in correct calls without force option."""
    random_src = Path("aba51e65-afd2-5020-8117-195f75e64258")
    random_dst = Path("f74d03de-7c1d-596f-83f3-73748f2e238f")

    watchmaker.utils.copytree(random_src, random_dst)

    # On Windows, a copy_function is always added; on other platforms it's not
    call_args = mock_copy.call_args
    assert call_args[0] == (random_src, random_dst)
    if platform.system() == "Windows":
        assert "copy_function" in call_args[1]
    else:
        assert call_args[1] == {}

    assert mock_rm.call_count == 0
    assert mock_exists.call_count == 0

    watchmaker.utils.copytree(random_src, random_dst, force=False)

    call_args = mock_copy.call_args
    assert call_args[0] == (random_src, random_dst)
    if platform.system() == "Windows":
        assert "copy_function" in call_args[1]
    else:
        assert call_args[1] == {}

    assert mock_rm.call_count == 0
    assert mock_exists.call_count == 0


@patch("pathlib.Path.exists", autospec=True)
@patch("shutil.rmtree", autospec=True)
@patch("shutil.copytree", autospec=True)
def test_copytree_force(mock_copy, mock_rm, mock_exists):
    """Test that copytree results in correct calls with force option."""
    random_src = Path("44b6df59-db6f-57cb-a570-ccd55d782561")
    random_dst = Path("72fe7962-a7af-5f2f-899b-54798bc5e79f")

    watchmaker.utils.copytree(random_src, random_dst, force=True)

    # On Windows, a copy_function is always added; on other platforms it's not
    call_args = mock_copy.call_args
    assert call_args[0] == (random_src, random_dst)
    if platform.system() == "Windows":
        assert "copy_function" in call_args[1]
    else:
        assert call_args[1] == {}

    mock_rm.assert_called_with(random_dst)
    mock_exists.assert_called_once()


def test_clean_none():
    """Check string 'None' conversion to None."""
    assert not watchmaker.utils.clean_none("None")
    assert not watchmaker.utils.clean_none("none")
    assert not watchmaker.utils.clean_none(None)
    assert watchmaker.utils.clean_none("not none") == "not none"


def test_uri_from_filepath_normalizes_file_uri(tmp_path):
    """Ensure file paths are normalized to canonical file URIs."""
    config_path = tmp_path / "config.yaml"
    assert (
        watchmaker.utils.uri_from_filepath(config_path)
        == config_path.resolve().as_uri()
    )


@patch("pathlib.Path.exists", autospec=True)
@patch("watchmaker.utils.copytree", autospec=True)
@patch("os.walk", autospec=True)
def test_copy_subdirectories(mock_os, mock_copy, mock_exists):
    """Test that copy_subdirectories executes expected calls."""
    random_src = Path("580a9176-20f6-4f64-b77a-75dbea14d74f")
    random_dst = Path("6538965c-5131-414a-897f-b01f7dfb6c2b")
    mock_exists.return_value = False
    # os.walk yields tuples where the first element (dirpath) is a string,
    # even if a Path was provided as input. Mock accordingly.
    mock_os.return_value = [
        (str(random_src), ("87a2a74d",)),
        (str(random_src / "87a2a74d"), (), ("6274fd83", "1923c65a")),
    ].__iter__()

    watchmaker.utils.copy_subdirectories(random_src, random_dst, None)
    assert mock_copy.call_count == 1


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Long path handling only applies on Windows",
)
@patch("shutil.copytree", autospec=True)
def test_copytree_windows_long_path(mock_copy):
    r"""Test copytree adds copy_function applying \\?\ prefix for long paths."""
    # Create a path that will exceed 200 characters when resolved
    long_component = "a" * 55
    long_src = (
        Path(long_component) / long_component / long_component / long_component / "src"
    )
    long_dst = (
        Path(long_component) / long_component / long_component / long_component / "dst"
    )

    watchmaker.utils.copytree(long_src, long_dst)

    # Verify a copy_function was added to the kwargs
    assert mock_copy.called
    call_kwargs = mock_copy.call_args[1]
    assert "copy_function" in call_kwargs

    # Test the copy_function with a long path (>200 chars)
    copy_func = call_kwargs["copy_function"]
    with patch("shutil.copy2") as mock_copy2:
        # Simulate a long file path
        long_file = str(Path("x" * 210) / "file.txt")
        copy_func(long_file, long_file + ".bak")

        # Verify copy2 was called with prefixed paths
        actual_src, actual_dst = mock_copy2.call_args[0]
        assert str(actual_src).startswith(r"\\?")
        assert str(actual_dst).startswith(r"\\?")


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Long path handling only applies on Windows",
)
@patch("shutil.copytree", autospec=True)
def test_copytree_windows_short_path_unchanged(mock_copy):
    """Test that copytree's copy_function preserves short paths without modification."""
    short_src = Path("short_src")
    short_dst = Path("short_dst")

    watchmaker.utils.copytree(short_src, short_dst)

    # Verify a copy_function was still added (always on Windows)
    assert mock_copy.called
    call_kwargs = mock_copy.call_args[1]
    assert "copy_function" in call_kwargs

    # Test the copy_function with a short path
    copy_func = call_kwargs["copy_function"]
    with patch("shutil.copy2") as mock_copy2:
        # Simulate a short file path
        short_file = "short_file.txt"
        copy_func(short_file, short_file + ".bak")

        # Verify copy2 was called with original paths (no \\?\ prefix)
        actual_src, actual_dst = mock_copy2.call_args[0]
        assert not str(actual_src).startswith(r"\\?")
        assert not str(actual_dst).startswith(r"\\?")


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Test non-Windows behavior",
)
@patch("shutil.copytree", autospec=True)
def test_copytree_non_windows_no_modification(mock_copy):
    """Test that copytree does not add copy_function on non-Windows systems."""
    # Even with a "long" path, no copy_function should be added on Linux/Mac
    long_component = "a" * 100
    long_src = Path(long_component) / long_component / "src"
    long_dst = Path(long_component) / long_component / "dst"

    watchmaker.utils.copytree(long_src, long_dst)

    # Verify no copy_function was added
    assert mock_copy.called
    call_kwargs = mock_copy.call_args[1]
    assert "copy_function" not in call_kwargs

    # Verify the paths were passed through unchanged
    mock_copy.assert_called_with(long_src, long_dst)
