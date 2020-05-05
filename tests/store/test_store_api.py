"""Tests for the store api"""
import datetime
import tempfile
from copy import deepcopy

from housekeeper.include import include_version


def test_fetch_bundles(populated_store, bundle_data_old):
    """
    test fetch all files when two bundles are added
    """
    store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj = store.add_bundle(data=bundle_data_old)[0]
    store.add_commit(bundle_old_obj)

    # WHEN fetching all files in the database
    query = store.files_before(before="2020-05-04")

    # THEN all four files should be fetched
    assert len(query.all()) == 4


def test_fetch_past_files(populated_store, bundle_data_old, timestamp, old_timestamp):
    """
    test fetch files where not all files are older than before date
    """
    store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj = store.add_bundle(data=bundle_data_old)[0]
    store.add_commit(bundle_old_obj)

    # WHEN fetching all files before the oldest date
    date = old_timestamp + datetime.timedelta(days=10)
    assert old_timestamp < date < timestamp
    query = store.files_before(before=str(date))

    # THEN assert only files from the old bundle was found
    assert len(query.all()) == 2


def test_fetch_no_files_before_oldest(
    populated_store, bundle_data_old, old_timestamp, timestamp
):
    """
    test fetch files where no files are older than before date
    """
    store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj = store.add_bundle(data=bundle_data_old)[0]
    store.add_commit(bundle_old_obj)

    # WHEN fetching all files before the oldest date
    date = old_timestamp - datetime.timedelta(days=10)
    assert date < old_timestamp < timestamp
    query = store.files_before(before=str(date))

    # THEN assert no files where that old
    assert len(query.all()) == 0


def test_delete_notondisk(store, project_dir, bundle_data):
    """
    test deletion of files that are not on disk
    """
    with tempfile.NamedTemporaryFile(delete=True) as file1:

        bundle_data_notondisk = deepcopy(bundle_data)
        bundle_data_notondisk["files"][0]["path"] = file1.name
        bundle_data_notondisk["files"][1]["path"] = bundle_data_notondisk["files"][1][
            "path"
        ].replace(".vcf", ".2.vcf")
        bundle_data_notondisk["name"] = "angrybird"

        bundle_obj, version_obj = store.add_bundle(data=bundle_data)
        store.add_commit(bundle_obj)
        include_version(project_dir, version_obj, hardlink=False)
        bundle_obj_notondisk, version_obj_notondisk = store.add_bundle(
            data=bundle_data_notondisk
        )
        store.add_commit(bundle_obj_notondisk)
        include_version(project_dir, version_obj_notondisk, hardlink=False)

    query = store.files_before()

    assert len(query.all()) == 4

    files_notondisk = set(query) - store.files_ondisk(query)

    assert len(files_notondisk) == 1
