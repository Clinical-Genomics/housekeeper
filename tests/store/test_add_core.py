"""Tests for store core functions"""

from housekeeper.store.models import Bundle, File, Tag, Version
from housekeeper.store.api.core import Store

# tag tests


def test_create_tag_obj(store: Store, vcf_tag_name):
    """Test to create a tag object"""
    # GIVEN a store and a tag name
    # WHEN creating a tag
    new_tag = store.new_tag(vcf_tag_name)
    # THEN assert a tag object was created
    assert isinstance(new_tag, Tag)
    assert new_tag.name == vcf_tag_name


def test_add_tag(store: Store, vcf_tag_obj):
    """Test to add a tag"""
    # GIVEN a store without tags
    assert store._get_query(table=Tag).count() == 0
    # WHEN adding a tag
    store.session.add(vcf_tag_obj)
    store.session.commit()
    # THEN assert the new tag was added
    assert store._get_query(table=Tag).count() == 1
    assert store._get_query(table=Tag).first() == vcf_tag_obj


# version tests


def test_create_version_obj(store: Store, timestamp):
    """Test to create a version object"""
    # GIVEN a store and a time stamp
    # WHEN creating a version
    new_version = store.new_version(created_at=timestamp, expires_at=timestamp)
    # THEN assert a version object was created
    assert isinstance(new_version, Version)
    assert new_version.created_at == timestamp


# bundle tests


def test_create_bundle_obj(store: Store, bundle_data):
    """Test to create a bundle object"""
    # GIVEN some bundle information
    # WHEN adding the new bundle
    bundle_obj = store.add_bundle(bundle_data)[0]
    # THEN the bundle should have correct name
    assert bundle_obj.name == bundle_data["name"]
    # THEN the bundle should have correct creation time
    assert bundle_obj.created_at == bundle_data["created_at"]
    # THEN assert that a version was added
    assert len(bundle_obj.versions) == 1
    # THEN assert that all files where added to the bundle
    assert len(bundle_obj.versions[0].files) == len(bundle_data["files"])


def test_add_bundle(store: Store, bundle_obj):
    """Test to add a bundle to the store"""
    # GIVEN a store without files, tags, versions or bundles
    assert store._get_query(table=Bundle).count() == 0
    assert store._get_query(table=Tag).count() == 0
    assert store._get_query(table=Version).count() == 0
    assert store._get_query(table=File).count() == 0
    # WHEN adding the new bundle
    store.session.add(bundle_obj)
    store.session.commit()
    # THEN assert that a bundle was added
    assert store._get_query(table=Bundle).count() == 1
    # THEN assert that the bundle is correct
    assert store._get_query(table=Bundle).first() == bundle_obj
    # THEN assert some tags where added
    assert store._get_query(table=Tag).count() > 0
    # THEN assert some files where added
    assert store._get_query(table=File).count() > 0
    # THEN assert we have a version
    assert store._get_query(table=Version).count() > 0


def test_add_bundle_twice(populated_store: Store, bundle_data):
    """Test to add a bundle twice"""
    store = populated_store
    # GIVEN a store ppopulated with a bundle
    assert store._get_query(table=Bundle).count() > 0
    # WHEN adding the same bundle again
    new_bundle = store.add_bundle(bundle_data)
    # THEN it should return None
    assert new_bundle is None


def test_add_two_versions_of_bundle(populated_store: Store, second_bundle_data):
    """Test to add two versions of the same bundle"""
    store: Store = populated_store
    # GIVEN a populated store and some modified bundle data
    assert store._get_query(table=Bundle).count() > 0

    # WHEN adding the modified bundle to the database
    new_bundle_obj = store.add_bundle(second_bundle_data)[0]
    store.session.add(new_bundle_obj)
    store.session.commit()

    # THEN there should still be one bundle
    assert store._get_query(table=Bundle).count() == 1
    # THEN there should be two versions
    assert store._get_query(table=Version).count() == 2
    # THEN tere should be all four files
    assert store._get_query(table=File).count() == 4
