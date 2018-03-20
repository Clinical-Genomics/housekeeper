# -*- coding: utf-8 -*-
import datetime

def test_delete_both(store, bundle_data, bundle_data_old):
    """
    """
    bundle_obj, version_obj = store.add_bundle(data=bundle_data)
    store.add_commit(bundle_obj)
    bundle_old_obj, version_old_obj = store.add_bundle(data=bundle_data_old)
    store.add_commit(bundle_old_obj)

    query = store.files_before(before=str(datetime.datetime.now()))
    assert len(query.all()) == 4
