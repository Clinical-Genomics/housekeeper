"""Tests for the add files method in store"""

from housekeeper.store import Store
from housekeeper.store.models import File, Tag, Bundle

from pathlib import Path
from typing import List


def test_add_file(populated_store: Store, second_family_vcf: Path, family_tag_names: List[str]):
    """Test to create a file with the add file method"""
    # GIVEN the path and the tags for a file

    # GIVEN a store populated with a bundle
    bundle: Bundle = populated_store.bundles().first()
    assert isinstance(bundle, Bundle)

    # WHEN using the add file method to create a new file object
    new_file: File = populated_store.add_file(
        file_path=second_family_vcf, bundle=bundle, tags=family_tag_names
    )

    # THEN assert that the file is a file object
    assert isinstance(new_file, File)
    # THEN assert that the file is added to the latest version of the bundle
    assert new_file.version == bundle.versions[0]
    # THEN assert that the tags are added to the new file
    assert len(new_file.tags) == len(family_tag_names)
    for tag_obj in new_file.tags:
        assert isinstance(tag_obj, Tag)


def test_add_file_no_tags(populated_store: Store, second_family_vcf: Path):
    """Test to create a file with the add file method without tags"""
    # GIVEN a path for a file

    # GIVEN a store populated with a bundle
    bundle: Bundle = populated_store.bundles().first()
    assert isinstance(bundle, Bundle)

    # WHEN using the add file method to create a new file object
    new_file = populated_store.add_file(file_path=second_family_vcf, bundle=bundle)

    # THEN assert that the no tags where added to the file
    assert len(new_file.tags) == 0
