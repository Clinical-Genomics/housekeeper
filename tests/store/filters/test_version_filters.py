from sqlalchemy.orm import Query

from housekeeper.store.filters.version_filters import filter_version_by_id
from housekeeper.store.models import Version
from housekeeper.store.store import Store


def test_get_version_query_returns_query_object(populated_store: Store):
    result = populated_store._get_query(table=Version)
    assert isinstance(result, Query)


def test_filter_version_by_id_returns_the_correct_version(populated_store: Store):
    """Test getting version by version ID."""

    # GIVEN a store with a version
    version: Version = populated_store._get_query(table=Version).first()
    assert version

    version_id: int = version.id

    # WHEN retrieving the version by ID
    filtered_version: Version = filter_version_by_id(
        versions=populated_store._get_query(table=Version),
        version_id=version_id,
    ).first()

    # THEN a version should be returned
    assert isinstance(filtered_version, Version)

    # THEN the id should match
    assert filtered_version.id == version_id


def test_filter_version_by_id_with_invalid_id_returns_empty_query(
    populated_store: Store,
):
    """Test that an empty result is returned when using an invalid version ID."""

    # GIVEN a store with versions
    versions_query = populated_store._get_query(table=Version)
    assert versions_query.count() > 0

    # GIVEN an invalid id that doesn't exist in the store
    non_existing_version_id = versions_query.order_by(Version.id.desc()).first().id + 1

    # WHEN filtering the versions by the invalid ID
    filtered_versions_query = filter_version_by_id(
        versions=versions_query, version_id=non_existing_version_id
    )

    # THEN the filtered query should be empty
    assert filtered_versions_query.count() == 0


def test_filter_version_by_id_with_empty_query_returns_empty_query(
    populated_store: Store,
):
    """Test that the function returns an empty result when given an empty query."""

    # GIVEN an empty query
    empty_query = populated_store._get_query(table=Version).filter(False)
    assert empty_query.count() == 0

    # WHEN filtering the empty query by an ID
    filtered_query = filter_version_by_id(versions=empty_query, version_id=1)

    # THEN the filtered query should still be empty
    assert filtered_query.count() == 0
