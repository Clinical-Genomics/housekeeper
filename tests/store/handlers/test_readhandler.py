"""Tests for finding tags in store."""
from datetime import timedelta
from pathlib import Path
from typing import List

from housekeeper.store import Store
from housekeeper.store.models import Tag, File


def test_tag_with_tag_name(populated_store: Store, sample_tag_name: str):
    """Test fetching a tag from database given a tag name."""
    # GIVEN a populated store and a tag name

    # WHEN retrieving a tag from Store
    test_tag = populated_store.get_tag(tag_name=sample_tag_name)

    # THEN a tag should be returned
    assert isinstance(test_tag, Tag)

    # THEN the tag should have the tag name gotten as parameter
    assert test_tag.name == sample_tag_name


def test_tag_without_tag_name(populated_store: Store):
    """Test fetching a tag from database without specifying a tag name returns None."""
    # GIVEN a populated store

    # WHEN retrieving a tag from Store
    test_tag = populated_store.get_tag()

    # THEN a tag should be returned
    assert test_tag is None


def test_get_files_before(populated_store, bundle_data_old, time_stamp_now):
    """
    Test return all files when two bundles are added and all files are older.
    """
    # GIVEN a populated store
    store: Store = populated_store
    starting_nr_of_files: int = len(store.get_files_before(before_date=time_stamp_now))

    # GIVEN two new files
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.session.add(bundle_old_obj)
    store.session.commit()

    # WHEN fetching all files in the database
    files = store.get_files_before(before_date=time_stamp_now)

    # THEN two more files should be returned
    assert len(files) == starting_nr_of_files + 2

def test_get_past_files(populated_store, bundle_data_old, timestamp, old_timestamp):
    """
    test fetch files where not all files are older than before date.
    """
    store: Store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.session.add(bundle_old_obj)
    store.session.commit()

    # WHEN fetching all files before the oldest date
    date = old_timestamp + timedelta(days=10)
    assert old_timestamp < date < timestamp
    files: List[File] = store.get_files_before(before_date=date)

    # THEN a list of Files is returned
    assert isinstance(files[0], File)

    # THEN assert only files from the old bundle was found
    assert len(files) == 2


def test_get_no_get_files_before_oldest(
    populated_store, bundle_data_old, old_timestamp, timestamp
):
    """
    Test get files where no files are older than before date.
    """
    store: Store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.session.add(bundle_old_obj)
    store.session.commit()

    # WHEN fetching all files before the oldest date
    date = old_timestamp - timedelta(days=10)
    assert date < old_timestamp < timestamp
    files: List[File] = store.get_files_before(before_date=date)

    # THEN assert no files where that old
    assert len(files) == 0


def test_get_archived_files(
    archived_file: Path,
    non_archived_file: Path,
    populated_store: Store,
    sample_id: str,
    spring_tag: str,
):
    """Tests fetching all archive SPRING files in a given bundle."""
    # GIVEN a bundle with two files, where one is archive and one is not

    # WHEN asking for all archived files
    archived_files: List[Path] = [
        Path(file.path)
        for file in populated_store.get_archived_files(
            bundle_name=sample_id, tags=[spring_tag]
        )
    ]

    # THEN only one should be returned
    assert archived_file in archived_files
    assert non_archived_file not in archived_files


def test_get_non_archived_files(
    archived_file: Path,
    non_archived_file: Path,
    populated_store: Store,
    sample_id: str,
    spring_tag: str,
):
    """Tests fetching all non-archive SPRING files in a given bundle."""
    # GIVEN a bundle with two files, where one is archive and one is not

    # WHEN asking for all non-archived files
    archived_files: List[Path] = [
        Path(file.path)
        for file in populated_store.get_non_archived_files(
            bundle_name=sample_id, tags=[spring_tag]
        )
    ]

    # THEN only one should be returned
    assert archived_file not in archived_files
    assert non_archived_file in archived_files
