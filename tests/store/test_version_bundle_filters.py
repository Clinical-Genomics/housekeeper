import datetime as dt
from sqlalchemy.orm import Query

from housekeeper.store.api.core import Store
from housekeeper.store.models import Bundle, Version
from housekeeper.store.version_bundle_filters import filter_version_by_name_and_bundle_date


def test_filter_version_by_name_and_bundle_date_returns_the_correct_version(populated_store: Store):
    """Test getting version by bundle name and date."""

    # GIVEN a store with some version
    version_bundles_query: Query =populated_store._get_version_bundle_query()
    assert version_bundles_query.count() > 0

    # GIVEN a bundle name and creation date
    bundle_name: str = version_bundles_query.first().bundle.name
    version_date: dt.datetime = version_bundles_query.first().created_at

    # WHEN filtering the version bundles by the given name and date
    filtered_version: Version = filter_version_by_name_and_bundle_date(
        version_bundles=populated_store._get_version_bundle_query(),
        bundle_name=bundle_name,
        version_date=version_date,
    ).first()

    # THEN a version should be returned
    assert isinstance(filtered_version, Version)

    # THEN the version's bundle name should match the given name
    assert filtered_version.bundle.name == bundle_name

    # THEN the version's creation date should match the given date
    assert filtered_version.created_at == version_date

def test_filter_version_by_name_and_bundle_date_with_nonexistent_data_returns_empty_query(populated_store):
    """Test that the function returns an empty result when given a non-existent bundle name or version date."""

    # GIVEN some bundle name and version date that does not exist in the store
    nonexistent_bundle_name = "nonexistent_bundle"
    nonexistent_version_date = dt.datetime.now()

    # WHEN filtering the versions by the nonexistent bundle name and version date
    filtered_version: Version = filter_version_by_name_and_bundle_date(
        version_bundles=populated_store._get_version_bundle_query(),
        bundle_name=nonexistent_bundle_name,
        version_date=nonexistent_version_date,
    )

    # THEN the filtered query should be empty
    assert filtered_version.count() == 0
