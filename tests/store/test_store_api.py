# -*- coding: utf-8 -*-
import os
import datetime
from copy import deepcopy

from pathlib import Path
import tempfile

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

    def include_version(global_root: str, version_obj):

        global_root_path = Path(global_root)
        version_root_dir = global_root_path / version_obj.relative_root_dir
        version_root_dir.mkdir(parents=True, exist_ok=True)

        for file_obj in version_obj.files:
            # softlink file to the internal structure
            new_path = version_root_dir / Path(file_obj.path).name
            os.symlink(Path(file_obj.path).resolve(), new_path)
            file_obj.path = str(new_path).replace(f"{global_root_path}/", '', 1)

    with tempfile.NamedTemporaryFile(delete=True) as file1:

        bundle_data_notondisk = deepcopy(bundle_data)
        bundle_data_notondisk['files'][0]['path']=file1.name
        bundle_data_notondisk['files'][1]['path']=bundle_data_notondisk['files'][1]['path'].replace('.vcf',
                                                                                    '.2.vcf')
        bundle_data_notondisk['name']='angrybird'

        bundle_obj, version_obj = store.add_bundle(data=bundle_data)
        store.add_commit(bundle_obj)
        include_version(tmpdir, version_obj)
        bundle_obj_notondisk, version_obj_notondisk = store.add_bundle(data=bundle_data_notondisk)
        store.add_commit(bundle_obj_notondisk)
        include_version(tmpdir, version_obj_notondisk)

    query = store.files_before()

    assert len(query.all()) == 4

    files_notondisk = set(query) - store.files_ondisk(query)

    assert len(files_notondisk) == 1
