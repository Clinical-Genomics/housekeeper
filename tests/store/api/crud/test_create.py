"""Tests for the functions in the store/api/crud/create.py module."""
from housekeeper.store import Store
from datetime import datetime
from housekeeper.store.models import Bundle


def test_create_bundle(store: Store, timestamp_now: datetime):
    """Test to create a bundle."""
    # GIVEN a store

    # WHEN creating a new bundle
    bundle: Bundle = store.create_bundle(name="bundle_name", created_at=timestamp_now)

    # THEN assert that the bundle was created with the correct name and timestamp
    assert bundle.name == "bundle_name"
    assert bundle.created_at == timestamp_now


def test_create_bundle_and_version_with_empty_store(
    store: Store, bundle_data: dict, case_id: str
):
    """Test to create a bundle and version."""
    # GIVEN a store
    assert store.get_bundles().count() == 0
    # WHEN creating a new bundle and version
    bundle, version = store.create_bundle_and_version(data=bundle_data)

    # THEN assert that the bundle and version was created with the correct name and timestamp
    assert bundle.name == case_id
    assert version.created_at == bundle_data["created_at"]
    assert bundle.versions[0].created_at == bundle_data["created_at"]
