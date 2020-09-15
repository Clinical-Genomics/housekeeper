"""Tests for the add files method in store"""

from housekeeper.store import models


def test_add_file(populated_store, second_family_vcf, family_tag_names):
    """Test to create a file with the add file method"""
    # GIVEN a store polulated with a bundle
    bundle_obj = populated_store.Bundle.query.first()
    # GIVEN some information about a file
    file_path = second_family_vcf
    tags = family_tag_names

    # WHEN using the add file method to create a new file object
    new_file = populated_store.add_file(
        file_path=file_path, bundle=bundle_obj, tags=tags
    )

    # THEN assert that the file is a file object
    assert isinstance(new_file, models.File)
    # THEN assert that the file is added to the latest version of the bundle
    assert new_file.version == bundle_obj.versions[0]
    # THEN assert that the tags are added to the new file
    assert len(new_file.tags) == len(tags)
    for tag_obj in new_file.tags:
        assert isinstance(tag_obj, models.Tag)


def test_add_file_no_tags(populated_store, second_family_vcf):
    """Test to create a file with the add file method without tags"""
    # GIVEN a store polulated with a bundle
    bundle_obj = populated_store.Bundle.query.first()
    # GIVEN some information about a file
    file_path = second_family_vcf

    # WHEN using the add file method to create a new file object
    new_file = populated_store.add_file(file_path=file_path, bundle=bundle_obj)

    # THEN assert that the no tags where added to the file
    assert len(new_file.tags) == 0
