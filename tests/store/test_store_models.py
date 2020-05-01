"""Tests for the models"""

from housekeeper.store import models


def test_instantiate_bundle(case_id, timestamp):
    """Test instantiate a Bundle object"""
    # GIVEN a case id and a time stamp
    # WHEN instantiating a bundle
    bundle_obj = models.Bundle(name=case_id, created_at=timestamp)
    # THEN assert it was instantiated as expected
    assert bundle_obj.name == case_id
    assert bundle_obj.created_at == timestamp


def test_version_obj_full_path(project_dir, store, bundle_obj):
    """Test the to get the full path from a version object"""
    # GIVEN a bundle object
    timestamp = bundle_obj.created_at
    # WHEN instantiating the version obj
    version_obj = models.Version(created_at=timestamp, bundle=bundle_obj)
    # THEN it should point to the correct folder
    root_path = version_obj.full_path
    assert root_path == project_dir / bundle_obj.name / str(timestamp.date())
