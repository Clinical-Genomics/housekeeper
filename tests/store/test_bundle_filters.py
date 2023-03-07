
from housekeeper.store import Store
from housekeeper.store.models import Bundle
from housekeeper.store.bundle_filters import filter_bundle_by_name, filter_bundle_by_id


def test_filter_bundles_by_id_returns_the_correct_bundle(populated_store: Store):
    """Test getting collaboration by internal_id."""

    # GIVEN a store with a bundle
    bundle: Bundle = populated_store.session.query(Bundle).first()
    assert bundle

    bundle_id: int = bundle.id

    # WHEN retrieving the bundle by id
    bundle: Bundle = filter_bundle_by_id(
        bundles=populated_store._get_bundle_query(),
        bundle_id=bundle_id,
    ).first()

    # THEN a bundle should be returned
    assert isinstance(bundle, Bundle)

    # THEN the id should match
    assert bundle.id == bundle_id

def test_filter_bundles_by_name_returns_the_correct_bundle(populated_store: Store):
    """Test getting bundle by name."""

    # GIVEN a store with a bundle
    bundle: Bundle = populated_store.session.query(Bundle).first()
    assert bundle

    bundle_name: str = bundle.name

    # WHEN retrieving the bundle by name
    bundle: Bundle = filter_bundle_by_name(
        bundles=populated_store._get_bundle_query(),
        bundle_name=bundle_name,
    ).first()

    # THEN a bundle should be returned
    assert isinstance(bundle, Bundle)

    # THEN the name should match
    assert bundle.name == bundle_name