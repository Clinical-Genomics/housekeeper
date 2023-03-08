"""Tests for the store api"""
import datetime


def test_fetch_bundles(populated_store, bundle_data_old):
    """
    test fetch all files when two bundles are added
    """
    store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    # WHEN fetching all files in the database
    files = store.files_before(before="2020-05-04")

    # THEN all four files should be fetched
    assert len(files) == 4


def test_fetch_past_files(populated_store, bundle_data_old, timestamp, old_timestamp):
    """
    test fetch files where not all files are older than before date
    """
    store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    # WHEN fetching all files before the oldest date
    date = old_timestamp + datetime.timedelta(days=10)
    assert old_timestamp < date < timestamp
    files = store.files_before(before=str(date))

    # THEN assert only files from the old bundle was found
    assert len(files) == 2


def test_fetch_no_files_before_oldest(populated_store, bundle_data_old, old_timestamp, timestamp):
    """
    test fetch files where no files are older than before date
    """
    store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    # WHEN fetching all files before the oldest date
    date = old_timestamp - datetime.timedelta(days=10)
    assert date < old_timestamp < timestamp
    files = store.files_before(before=str(date))

    # THEN assert no files where that old
    assert len(files) == 0
