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
    bundle_obj, version_obj = store.add_bundle(data=bundle_data)
    store.add_commit(bundle_obj)
    bundle_old_obj, version_old_obj = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    query = store.files_before(before=str(datetime.datetime.now()))
    assert len(query.all()) == 4


def test_delete_one(store, bundle_data, bundle_data_old):
    """
    test deletion where not all files are older than before date
    """
    bundle_obj, version_obj = store.add_bundle(data=bundle_data)
    store.add_commit(bundle_obj)
    bundle_old_obj, version_old_obj = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    query = store.files_before(before="2018-02-01")
    assert len(query.all()) == 2


def test_delete_none(store, bundle_data, bundle_data_old):
    """
    test deletion where no files are older than before date
    """
    bundle_obj, version_obj = store.add_bundle(data=bundle_data)
    store.add_commit(bundle_obj)
    bundle_old_obj, version_old_obj = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    query = store.files_before(before="2017-02-01")
    assert len(query.all()) == 0


def test_delete_notondisk(store, tmpdir, bundle_data):
    """
    test deletion of files that are not on disk
    """
    with tempfile.NamedTemporaryFile(delete=True) as file1:

        bundle_data_notondisk = deepcopy(bundle_data)
        bundle_data_notondisk['files'][0]['path']=file1.name
        bundle_data_notondisk['files'][1]['path']=bundle_data_notondisk['files'][1]['path'].replace('.vcf',
                                                                                    '.2.vcf')
        bundle_data_notondisk['name']='angrybird'

        bundle_obj, version_obj = store.add_bundle(data=bundle_data)
        store.add_commit(bundle_obj)
        include_version(tmpdir, version_obj, hardlink=False)
        bundle_obj_notondisk, version_obj_notondisk = store.add_bundle(data=bundle_data_notondisk)
        store.add_commit(bundle_obj_notondisk)
        include_version(tmpdir, version_obj_notondisk, hardlink=False)

    query = store.files_before()

    assert len(query.all()) == 4

    files_notondisk = set(query) - store.files_ondisk(query)

    assert len(files_notondisk) == 1
