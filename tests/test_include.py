"""Tests for the include module"""

import datetime
from pathlib import Path

import pytest

from housekeeper import include
from housekeeper.exc import VersionIncludedError
from housekeeper.store import models


def test_checksum(checksum: str, checksum_file: Path):
    """Test calculate checksum"""
    # GIVEN a file with a specific checksum

    # WHEN calculating the checksum
    calculated_checksum = include.checksum(checksum_file)

    # THEN it should match
    assert calculated_checksum == checksum


def test_include_version(project_dir: Path, version_obj: models.Version):
    """Test to include a version

    This should test if hardlinks where created when running the include function
    """
    global_root_path = project_dir
    version = version_obj
    # GIVEN a new directory as the global root
    file_names = [Path(file_obj.path).name for file_obj in version.files]
    date_str = str(version.created_at.date())
    assert len(list(global_root_path.iterdir())) == 0

    # WHEN including a bundle version
    include.include_version(str(global_root_path), version)

    # THEN it should link the files to the new destination
    version_root_path = global_root_path / version.bundle.name / date_str
    assert len(list(version_root_path.iterdir())) == len(version.files)
    for file_obj, file_name in zip(version.files, file_names):
        # ... and the file path should be replace with relative "internal" path
        assert (global_root_path / file_obj.path).exists()
        assert (global_root_path / file_obj.path).is_file()
        assert Path(file_obj.path) == Path(version.bundle.name) / date_str / file_name


def test_include_version_already_included(project_dir: Path, version_obj: models.Version):
    """Test to include files from version when they where already included"""
    # GIVEN a version which is already marked as included
    version_obj.included_at = datetime.datetime.now()

    # WHEN trying to "include it"
    with pytest.raises(VersionIncludedError):
        # THEN it should raise an exception
        include.include_version(project_dir, version_obj)
