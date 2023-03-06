
from housekeeper.store import Store
from housekeeper.store.models import Bundle
from housekeeper.store.bundle_filters import filter_bundle_by_name, filter_bundle_by_id


def test_filter_bundles_by_id(populated_store: Store):
    """Test getting collaboration by internal_id."""
    # GIVEN a store with a bundle
    bundle_id: int = 1
    # WHEN retrieving the bundle by id
    bundle: Bundle = filter_bundle_by_id(
        bundles=populated_store._get_bundle_query(),
        bundle_id=bundle_id,
    ).first()

    # THEN bundle should be returned
    assert bundle

    # THEN the internal_id should match the fixture
    assert bundle.id == bundle_id

def test_filter_bundles_by_name(populated_store: Store, case_id: str):
    """Test getting bundle by name."""
    # GIVEN a store with a bundle

    # WHEN retrieving the bundle by name
    bundle: Bundle = filter_bundle_by_name(
        bundles=populated_store._get_bundle_query(),
        bundle_name=case_id,
    ).first()

    # THEN bundle should be returned
    assert bundle

    # THEN the internal_id should match the fixture
    assert bundle.name == case_id
