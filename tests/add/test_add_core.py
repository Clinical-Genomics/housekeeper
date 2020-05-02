"""Tests for store core functions"""
import datetime
from copy import deepcopy

from housekeeper.store import models

# tag tests


def test_create_tag(store, vcf_tag_name):
    """Test to add a tag"""
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


def test_create_version(store, timestamp):
    """Test to create a version object"""
    # GIVEN a store and a time stamp
    # WHEN creating a version
    new_version = store.new_version(created_at=timestamp, expires_at=timestamp)
    # THEN assert a version object was created
    assert isinstance(new_version, models.Version)
    assert new_version.created_at == timestamp


def test_add_bundle(store, bundle_data):
    # GIVEN a store without files, tags or bundles
    assert store.Bundle.query.count() == 0
    assert store.Tag.query.count() == 0
    assert store.Version.query.count() == 0
    # WHEN adding the new bundle
    bundle_obj, version_obj = store.add_bundle(bundle_data)
    # THEN it should look as expected
    assert bundle_obj.name == bundle_data["name"]
    assert bundle_obj.created_at == bundle_data["created"]
    assert bundle_obj.versions[0].created_at == bundle_data["created"]
    assert bundle_obj.versions[0].expires_at == bundle_data["expires"]
    assert len(bundle_obj.versions[0].files) == len(bundle_data["files"])
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
    bundle_2["created"] = datetime.datetime.now()
    for file_data in bundle_2["files"]:
        file_data["path"] = file_data["path"].replace(".vcf", ".2.vcf")
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


def test_rna_add_one_file_per_type(store, rna_bundle_data_one_file):
    # GIVEN one file for a given file type
    assert isinstance(rna_bundle_data_one_file["files"][0]["path"], str)

    # WHEN adding the path to the version object
    bundle_obj, version_obj = store.add_bundle(rna_bundle_data_one_file)

    # THEN that one file should be added to the version object
    assert len(version_obj.files) == 1
    assert version_obj.files[0]["path"] == rna_bundle_data_one_file["files"][0]["path"]
    assert version_obj.bundle == bundle_obj


def test_rna_add_two_files_per_type(store, rna_bundle_data_two_files):
    # GIVEN two files for a given file type
    assert isinstance(rna_bundle_data_two_files["files"][0]["path"], list)

    # WHEN adding the paths to the version object
    bundle_obj, version_obj = store.add_bundle(rna_bundle_data_two_files)

    # THEN that both files should be added to the version object
    assert len(version_obj.files) == 2
    assert (
        version_obj.files[0]["path"] == rna_bundle_data_two_files["files"][0]["path"][0]
    )
    assert (
        version_obj.files[1]["path"] == rna_bundle_data_two_files["files"][0]["path"][1]
    )
    assert version_obj.bundle == bundle_obj
