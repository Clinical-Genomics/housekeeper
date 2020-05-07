"""Tests for the models"""

from housekeeper.store import models


def test_instantiate_bundle_obj(case_id, timestamp):
    """Test instantiate a Bundle object"""
    # GIVEN a case id and a time stamp
    # WHEN instantiating a bundle
    bundle_obj = models.Bundle(name=case_id, created_at=timestamp)
    # THEN assert it was instantiated as expected
    assert bundle_obj.name == case_id
    assert bundle_obj.created_at == timestamp


def test_instantiate_bundle_obj_no_name():
    """Test instantiate a Bundle object without a name"""
    # WHEN instantiating a bundle without a name
    bundle_obj = models.Bundle()
    # THEN assert it was instantiated as expected
    assert bundle_obj.name is None
    assert bundle_obj.versions == []


def test_version_obj_full_path(project_dir, minimal_bundle_obj):
    """Test the to get the full path from a version object"""
    # GIVEN a bundle object
    timestamp = minimal_bundle_obj.created_at
    # WHEN instantiating the version obj
    version_obj = models.Version(created_at=timestamp, bundle=minimal_bundle_obj)
    # THEN it should point to the correct folder
    root_path = version_obj.full_path
    assert root_path == project_dir / minimal_bundle_obj.name / str(timestamp.date())
