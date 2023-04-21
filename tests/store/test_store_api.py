"""Tests for the store api"""
import datetime
from typing import List
from housekeeper.store.api.core import Store

from housekeeper.store.models import File


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
    date = old_timestamp + datetime.timedelta(days=10)
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
    date = old_timestamp - datetime.timedelta(days=10)
    assert date < old_timestamp < timestamp
    files: List[File] = store.get_files_before(before_date=date)

    # THEN assert no files where that old
    assert len(files) == 0
