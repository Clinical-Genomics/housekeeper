# -*- coding: utf-8 -*-
from copy import deepcopy
import datetime


def test_build_tags(store):
    # GIVEN a store with some tags
    tag_names = ['vcf', 'family']
    new_tag = store.new_tag(tag_names[0])
    store.add_commit(new_tag)
    assert store.Tag.query.count() == 1
    assert store.Tag.query.first() == new_tag
    # WHEN adding tags...
    tag_map = store._build_tags(tag_names)
    # THEN it should return the existing tag
    assert len(tag_map) == len(tag_names)
    assert tag_map[tag_names[0]].name == tag_names[0]
    # ... and build the missing tag
    assert tag_map[tag_names[1]].name == tag_names[1]
    # which can be committed to the database
    assert store.Tag.query.count() == 1
    store.add_commit(list(tag_map.values()))
    assert store.Tag.query.count() == 2


def test_add_bundle(store, bundle_data):
    # GIVEN some input data for a new bundle
    assert store.Bundle.query.count() == 0
    # WHEN adding the new bundle
    bundle_obj, version_obj = store.add_bundle(bundle_data)
    # THEN it should look as expected
    assert bundle_obj.name == bundle_data['name']
    assert bundle_obj.created_at == bundle_data['created']
    assert bundle_obj.versions[0].created_at == bundle_data['created']
    assert bundle_obj.versions[0].expires_at == bundle_data['expires']
    assert len(bundle_obj.versions[0].files) == len(bundle_data['files'])
    # ... and you should be able to commit the record in one go!
    store.add_commit(bundle_obj)
    assert store.Bundle.query.count() == 1
    assert store.Bundle.query.first() == bundle_obj
    assert store.Tag.query.count() == 3
    assert store.File.query.count() == 2


def test_add_bundle_twice(store, bundle_data):
    # GIVEN a bundle in the store
    bundle_obj, version_obj = store.add_bundle(bundle_data)
    store.add_commit(bundle_obj)
    assert store.Bundle.query.first() == bundle_obj
    # WHEN adding the same bundle again
    # THEN it should return None
    new_bundle = store.add_bundle(bundle_data)
    assert new_bundle is None
    assert store.Bundle.query.count() == 1


def test_add_two_versions_of_bundle(store, bundle_data):
    # GIVEN two versions of the same bundle
    assert store.Bundle.query.count() == 0
    bundle_1 = bundle_data
    bundle_2 = deepcopy(bundle_data)
    bundle_2['created'] = datetime.datetime.now()
    for file_data in bundle_2['files']:
        file_data['path'] = file_data['path'].replace('.vcf', '.2.vcf')
    # WHEN adding them to the database
    with store.session.no_autoflush:
        for bundle in [bundle_1, bundle_2]:
            bundle_obj, version_obj = store.add_bundle(bundle)
            store.add_commit(bundle_obj)

    # THEN it should only create a single bundle
    assert store.Bundle.query.count() == 1
    # ... but two versions
    assert store.Version.query.count() == 2
    # ... and all four files
    assert store.File.query.count() == 4
