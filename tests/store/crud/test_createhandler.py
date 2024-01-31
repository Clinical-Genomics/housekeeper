"""Tests for store core functions."""

from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError

from housekeeper.store.api import schema
from housekeeper.store.models import Archive, Bundle, File, Tag, Version
from housekeeper.store.store import Store


def test_schema_with_invalid_input(bundle_data_json):
    """Tests that errors are thrown when validating incorrect input data."""
    # GIVEN input data with missing name of the bundle
    del bundle_data_json["name"]
    # WHEN validating it against the schema
    errors = schema.BundleSchema().validate(bundle_data_json)
    # THEN it should report errors for the field
    assert len(errors) > 0
    assert "name" in errors


# tag tests


def test_create_tag_obj(store: Store, vcf_tag_name):
    """Test to create a tag object."""
    # GIVEN a store and a tag name
    # WHEN creating a tag
    new_tag = store.new_tag(vcf_tag_name)
    # THEN assert a tag object was created
    assert isinstance(new_tag, Tag)
    assert new_tag.name == vcf_tag_name


def test_add_tag(store: Store, vcf_tag_obj):
    """Test to add a tag."""
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
    """Test to create a version object."""
    # GIVEN a store and a time stamp
    # WHEN creating a version
    new_version = store.new_version(created_at=timestamp, expires_at=timestamp)
    # THEN assert a version object was created
    assert isinstance(new_version, Version)
    assert new_version.created_at == timestamp


# bundle tests


def test_create_bundle_obj(store: Store, bundle_data):
    """Test to create a bundle object."""
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
    """Test to add a bundle to the store."""
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
    """Test to add a bundle twice."""
    store = populated_store
    # GIVEN a store ppopulated with a bundle
    assert store._get_query(table=Bundle).count() > 0
    # WHEN adding the same bundle again
    new_bundle = store.add_bundle(bundle_data)
    # THEN it should return None
    assert new_bundle is None


def test_add_two_versions_of_bundle(populated_store: Store, second_bundle_data: dict):
    """Test to add two versions of the same bundle."""
    store: Store = populated_store
    # GIVEN a populated store and some modified bundle data
    starting_bundle_count: int = store._get_query(table=Bundle).count()
    starting_version_count: int = store._get_query(table=Version).count()
    starting_file_count: int = store._get_query(table=File).count()

    # WHEN adding the modified bundle to the database
    new_bundle_obj, version = store.add_bundle(second_bundle_data)
    store.session.add(new_bundle_obj)
    store.session.add(version)
    store.session.commit()

    # THEN there should still be the same number of bundles
    assert store._get_query(table=Bundle).count() == starting_bundle_count
    # THEN there should be one more version
    assert store._get_query(table=Version).count() == starting_version_count + 1
    # THEN there should be two more files
    assert store._get_query(table=File).count() == starting_file_count + 2


def test_add_archive(archiving_task_id: int, populated_store: Store, spring_file_2: Path):
    """Test that adding an archive works as expected."""
    # GIVEN a file that is not archived
    non_archived_file: File = populated_store.get_files(file_path=spring_file_2.as_posix()).first()
    # WHEN adding an archive
    new_archive: Archive = populated_store.create_archive(
        file_id=non_archived_file.id, archiving_task_id=archiving_task_id
    )
    populated_store.session.add(new_archive)
    populated_store.session.commit()
    # THEN an archive should be created
    assert isinstance(new_archive, Archive)
    # THEN the archive should be reachable via the file
    assert non_archived_file.archive == new_archive


def test_add_archive_to_archived_file(
    archiving_task_id: int, populated_store: Store, spring_file_1: Path
):
    """Test that adding an archive to an already archived file raises an error."""
    # GIVEN a file that is archived
    non_archived_file: File = populated_store.get_files(file_path=spring_file_1.as_posix()).first()
    # WHEN adding an archive
    new_archive: Archive = populated_store.create_archive(
        file_id=non_archived_file.id, archiving_task_id=archiving_task_id
    )
    populated_store.session.add(new_archive)

    # THEN an SQLAlchemy error should be thrown
    with pytest.raises(IntegrityError):
        populated_store.session.commit()


def test_add_file(
    populated_store: Store,
    second_family_vcf: Path,
    family_tag_names: list[str],
    housekeeper_version_dir: Path,
    project_dir: Path,
):
    """Test to create a file with the add file method."""
    # GIVEN the path and the tags for a file

    # GIVEN a store populated with a bundle
    bundle: Bundle = populated_store.bundles().first()
    assert isinstance(bundle, Bundle)

    # WHEN using the add file method to create a new file object
    new_file: File = populated_store.add_file(
        file_path=second_family_vcf,
        bundle=bundle,
        tags=family_tag_names,
    )

    # THEN assert that the file is a file object
    assert isinstance(new_file, File)
    # THEN assert that the file is added to the latest version of the bundle
    assert new_file.version == bundle.versions[0]
    # THEN assert that the tags are added to the new file
    assert len(new_file.tags) == len(family_tag_names)
    for tag_obj in new_file.tags:
        assert isinstance(tag_obj, Tag)


def test_add_file_no_tags(
    populated_store: Store,
    second_family_vcf: Path,
    housekeeper_version_dir: Path,
    project_dir: Path,
):
    """Test to create a file with the add file method without tags."""
    # GIVEN a path for a file

    # GIVEN a store populated with a bundle
    bundle: Bundle = populated_store.bundles().first()
    assert isinstance(bundle, Bundle)

    # WHEN using the add file method to create a new file object
    new_file = populated_store.add_file(file_path=second_family_vcf, bundle=bundle)

    # THEN assert that the no tags where added to the file
    assert len(new_file.tags) == 0
