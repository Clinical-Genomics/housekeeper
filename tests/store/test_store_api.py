# -*- coding: utf-8 -*-
import datetime


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


def test_delete_notondisk(store, bundle_data, bundle_data_old):
    """
    test deletion of files that are not on disk
    """
    pass
