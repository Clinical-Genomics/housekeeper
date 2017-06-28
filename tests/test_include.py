# -*- coding: utf-8 -*-
import datetime
from pathlib import Path

import pytest

from housekeeper import include
from housekeeper.exc import VersionIncludedError


def test_checksum():
    # GIVEN a file with a specific checksum
    file_path = Path('tests/fixtures/26a90105b99c05381328317f913e9509e373b64f.txt')
    expected_checksum = file_path.name.rstrip('.txt')
    # WHEN calculating the checksum
    checksum = include.checksum(file_path)
    # THEN it should match
    assert checksum == expected_checksum


def test_include_version(tmpdir, version):
    # GIVEN a new directory as the global root
    global_root = tmpdir.mkdir('destination')
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
