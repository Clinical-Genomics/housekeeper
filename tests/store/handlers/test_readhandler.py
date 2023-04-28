"""Tests for finding tags in store."""
from datetime import datetime, timedelta
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
    Test return all files when two bundles are added.
    """
    store: Store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.session.add(bundle_old_obj)
    store.session.commit()

    # WHEN fetching all files in the database
    files = store.get_files_before(before_date=time_stamp_now)

    # THEN all four files should be fetched
    assert len(files) == 4


def test_get_past_files(populated_store, bundle_data_old, timestamp, old_timestamp):
    """
    test fetch files where not all files are older than before date
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
