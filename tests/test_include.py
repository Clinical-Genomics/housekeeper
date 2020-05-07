"""Tests for the include module"""
import datetime
from pathlib import Path

import pytest

from housekeeper import include
from housekeeper.exc import VersionIncludedError


def test_checksum(checksum, checksum_file):
    """Test calculate checksum"""
    # GIVEN a file with a specific checksum
    # WHEN calculating the checksum
    calculated_checksum = include.checksum(checksum_file)
    # THEN it should match
    assert calculated_checksum == checksum


def test_include_version(tmpdir, version):
    # GIVEN a new directory as the global root
    global_root = tmpdir.mkdir("destination")
    global_root_path = Path(global_root)
    file_names = [Path(file_obj.path).name for file_obj in version.files]
    date_str = str(version.created_at.date())
    assert len(list(global_root_path.iterdir())) == 0
    # WHEN including a bundle version
    include.include_version(global_root, version)
    # THEN it should link the files to the new destination
    version_root_path = global_root_path / version.bundle.name / date_str
    assert len(list(version_root_path.iterdir())) == len(version.files)
    for file_obj, file_name in zip(version.files, file_names):
        # ... and the file path should be replace with relative "internal" path
        assert (global_root_path / file_obj.path).exists()
        assert (global_root_path / file_obj.path).is_file()
        assert Path(file_obj.path) == Path(version.bundle.name) / date_str / file_name
        # ... and it should fill-in the checksum
        if file_obj.to_archive:
            assert isinstance(file_obj.checksum, str)
        else:
            assert file_obj.checksum is None


def test_include_version_already_included(tmpdir, version):
    # GIVEN a version which is already marked as included
    version.included_at = datetime.datetime.now()
    # WHEN trying to "include it"
    # THEN it should raise an exception
    with pytest.raises(VersionIncludedError):
        include.include_version(tmpdir, version)
