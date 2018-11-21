# -*- coding: utf-8 -*-
import os
import datetime
from copy import deepcopy

from pathlib import Path
import tempfile

from housekeeper.include import include_version

def test_delete_both(store, bundle_data, bundle_data_old):
    """
    test deletion where all files are older than before date
    """

    # GIVEN two bundles with different creation dates and each two files
    bundle_obj, version_obj = store.add_bundle(data=bundle_data)
    store.add_commit(bundle_obj)
    bundle_old_obj, version_old_obj = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    # WHEN we query for files before now
    query = store.files_before(before=str(datetime.datetime.now()))

    # THEN we should be able to count all files
    assert len(query.all()) == 4


def test_delete_one(store, bundle_data, bundle_data_old):
    """
    test deletion where not all files are older than before date
    """

    # GIVEN two bundles with different creation dates and each two files
    bundle_obj, version_obj = store.add_bundle(data=bundle_data)
    store.add_commit(bundle_obj)
    bundle_old_obj, version_old_obj = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    # WHEN we query for all files before just one of the bundles' creation date
    query = store.files_before(before="2018-02-01")

    # THEN we should be able to count two out of four files
    assert len(query.all()) == 2


def test_delete_none(store, bundle_data, bundle_data_old):
    """
    test deletion where no files are older than before date
    """
    # GIVEN two bundles with two different creation dates
    bundle_obj, version_obj = store.add_bundle(data=bundle_data)
    store.add_commit(bundle_obj)
    bundle_old_obj, version_old_obj = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    # WHEN we query for files stored before their creation date
    query = store.files_before(before="2017-02-01")

    # THEN we should not find any files!
    assert len(query.all()) == 0


def test_delete_notondisk(store, tmpdir, bundle_data):
    """
    test deletion of files that are not on disk
    """
    # GIVEN two bundles: one with files on disk and one without
    with tempfile.NamedTemporaryFile(delete=True) as file1:

        # WHEN the files in the bundle are not on disk
        bundle_data_notondisk = deepcopy(bundle_data)
        bundle_data_notondisk['files'][0]['path'] = file1.name
        bundle_data_notondisk['files'][1]['path'] = bundle_data_notondisk['files'][1]['path'].replace('.vcf',
                                                                                    '.2.vcf')
        bundle_data_notondisk['name'] = 'angrybird'

        bundle_obj, version_obj = store.add_bundle(data=bundle_data)
        include_version(tmpdir, version_obj, hardlink=False)
        store.add_commit(bundle_obj)
        bundle_obj_notondisk, version_obj_notondisk = store.add_bundle(data=bundle_data_notondisk)
        include_version(tmpdir, version_obj_notondisk, hardlink=False)
        store.add_commit(bundle_obj_notondisk)

    query = store.files_before()
    files_notondisk = set(query) - store.files_ondisk(query)

    # THEN the amount of files listed in the database ...
    assert len(query.all()) == 4
    # ... should be different than the files on disk
    assert len(files_notondisk) == 1
