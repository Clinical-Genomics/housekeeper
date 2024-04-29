"""Tests for the models"""

from housekeeper.store.models import Archive, Bundle, Version
from housekeeper.store.store import Store


def test_instantiate_bundle_obj(case_id, timestamp):
    """Test instantiate a Bundle object"""
    # GIVEN a case id and a time stamp
    # WHEN instantiating a bundle
    bundle_obj = Bundle(name=case_id, created_at=timestamp)
    # THEN assert it was instantiated as expected
    assert bundle_obj.name == case_id
    assert bundle_obj.created_at == timestamp


def test_instantiate_bundle_obj_no_name():
    """Test instantiate a Bundle object without a name"""
    # WHEN instantiating a bundle without a name
    bundle_obj = Bundle()
    # THEN assert it was instantiated as expected
    assert bundle_obj.name is None
    assert bundle_obj.versions == []


def test_version_obj_full_path(project_dir, minimal_bundle_obj):
    """Test returning the full path from a version object"""
    # GIVEN a bundle object
    timestamp = minimal_bundle_obj.created_at
    # WHEN instantiating the version obj
    version_obj = Version(created_at=timestamp, bundle=minimal_bundle_obj)
    # THEN it should point to the correct folder
    root_path = version_obj.full_path
    assert root_path == project_dir / minimal_bundle_obj.name / str(timestamp.date())


def test_delete_file_cascades(archive: Archive, populated_store: Store):
    """Tests that deleting a file deletes the associated archive entry."""

    # GIVEN an archive entry
    archive_task_id: int = archive.archiving_task_id
    file_id: int = archive.file.id

    # WHEN the file is deleted
    populated_store.session.delete(archive.file)
    populated_store.session.commit()

    # THEN the archive entry should be deleted
    for archive_entry in populated_store.get_archives(archival_task_id=archive_task_id):
        assert archive_entry.file.id != file_id


def test_delete_archive_does_not_cascade(archive: Archive, populated_store: Store):
    """Tests that deleting an archive entry does not delete the file entry."""

    # GIVEN an archive entry
    file_path: str = archive.file.path

    # WHEN deleting the archive entry
    populated_store.session.delete(archive)
    populated_store.session.commit()

    # THEN the file should still be in the store
    assert populated_store.get_files(file_path=file_path)
