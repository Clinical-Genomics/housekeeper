"""Tests for store core functions"""

from housekeeper.store import models

# tag tests


def test_create_tag_obj(store, vcf_tag_name):
    """Test to create a tag object"""
    # GIVEN a store and a tag name
    # WHEN creating a tag
    new_tag = store.new_tag(vcf_tag_name)
    # THEN assert a tag object was created
    assert isinstance(new_tag, models.Tag)
    assert new_tag.name == vcf_tag_name


def test_add_tag(store, vcf_tag_obj):
    """Test to add a tag"""
    # GIVEN a store without tags
    assert store.Tag.query.count() == 0
    # WHEN adding a tag
    store.add_commit(vcf_tag_obj)
    # THEN assert the new tag was added
    assert store.Tag.query.count() == 1
    assert store.Tag.query.first() == vcf_tag_obj


# version tests


def test_create_version_obj(store, timestamp):
    """Test to create a version object"""
    # GIVEN a store and a time stamp
    # WHEN creating a version
    new_version = store.new_version(created_at=timestamp, expires_at=timestamp)
    # THEN assert a version object was created
    assert isinstance(new_version, models.Version)
    assert new_version.created_at == timestamp


# bundle tests


def test_create_bundle_obj(store, bundle_data):
    """Test to create a bundle object"""
    # GIVEN some bundle information
    # WHEN adding the new bundle
    bundle_obj = store.add_bundle(bundle_data)[0]
    # THEN the bundle should have correct name
    assert bundle_obj.name == bundle_data["name"]
    # THEN the bundle should have correct creation time
    assert bundle_obj.created_at == bundle_data["created"]
    # THEN assert that a version was added
    assert len(bundle_obj.versions) == 1
    # THEN assert that all files where added to the bundle
    assert len(bundle_obj.versions[0].files) == len(bundle_data["files"])


def test_add_bundle(store, bundle_obj):
    """Test to add a bundle to the store"""
    # GIVEN a store without files, tags, versions or bundles
    assert store.Bundle.query.count() == 0
    assert store.Tag.query.count() == 0
    assert store.Version.query.count() == 0
    assert store.File.query.count() == 0
    # WHEN adding the new bundle
    store.add_commit(bundle_obj)
    # THEN assert that a bundle was added
    assert store.Bundle.query.count() == 1
    # THEN assert that the bundle is correct
    assert store.Bundle.query.first() == bundle_obj
    # THEN assert some tags where added
    assert store.Tag.query.count() > 0
    # THEN assert some files where added
    assert store.File.query.count() > 0
    # THEN assert we have a version
    assert store.Version.query.count() > 0


def test_add_bundle_twice(populated_store, bundle_data):
    """Test to add a bundle twice"""
    store = populated_store
    # GIVEN a store ppopulated with a bundle
    assert store.Bundle.query.count() > 0
    # WHEN adding the same bundle again
    new_bundle = store.add_bundle(bundle_data)
    # THEN it should return None
    assert new_bundle is None


def test_add_two_versions_of_bundle(populated_store, second_bundle_data):
    """Test to add two versions of the same bundle"""
    store = populated_store
    # GIVEN a populated store and some modified bundle data
    assert store.Bundle.query.count() > 0

    # WHEN adding the modified bundle to the database
    new_bundle_obj = store.add_bundle(second_bundle_data)[0]
    store.add_commit(new_bundle_obj)

    # THEN there should still be one bundle
    assert store.Bundle.query.count() == 1
    # THEN there should be two versions
    assert store.Version.query.count() == 2
    # THEN tere should be all four files
    assert store.File.query.count() == 4
