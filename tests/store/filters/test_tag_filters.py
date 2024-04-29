from sqlalchemy.orm import Query

from housekeeper.store.filters.tag_filters import (
    TagFilter,
    apply_tag_filter,
    filter_tag_by_name,
)
from housekeeper.store.models import Tag
from housekeeper.store.store import Store


def test_filter_tag_by_name_returns_correct_tag(populated_store: Store, sample_tag_name: str):
    """Test that fetching a tag by name returns a tag with the expected name."""

    # GIVEN a store with the desired tag
    all_tags: Query = populated_store._get_query(table=Tag)
    all_tag_names: list[str] = [t.name for t in all_tags.all()]
    assert sample_tag_name in all_tag_names

    # WHEN retrieving the tag by name
    tag_query: Tag = filter_tag_by_name(
        tags=all_tags,
        tag_name=sample_tag_name,
    )
    tag: Tag = tag_query.first()

    # THEN the returned object is a Query
    assert isinstance(tag_query, Query)

    # THEN the object in the query is a Tag
    assert isinstance(tag, Tag)

    # THEN the tag name should match the input tag name
    assert tag.name == sample_tag_name


def test_filter_tag_by_name_non_existent_tag(populated_store: Store, non_existent_tag_name):
    """Test that using a non-existent tag name returns an empty query."""
    # GIVEN a tag name not included in a populated store
    all_tags: Query = populated_store._get_query(table=Tag)
    all_tag_names: list[str] = [t.name for t in all_tags.all()]
    assert non_existent_tag_name not in all_tag_names

    # WHEN retrieving the tag by name
    tag_query: Query = filter_tag_by_name(
        tags=all_tags,
        tag_name=non_existent_tag_name,
    )
    assert isinstance(tag_query, Query)

    # THEN the retrieved query is empty
    assert tag_query.count() == 0


def test_filter_tag_by_name_with_none_tag_name(populated_store: Store):
    """Test that using None as tag name argument returns an empty query."""
    # GIVEN a populated store

    # WHEN trying to retrieve a tag with None as name
    tag_query: Query = filter_tag_by_name(
        tags=populated_store._get_query(table=Tag),
        tag_name=None,
    )
    assert isinstance(tag_query, Query)

    # THEN the retrieved query is empty
    assert tag_query.count() == 0


def test_apply_tag_filter_without_tag_name(populated_store: Store):
    """Test that omitting the tag name argument returns an empty query"""
    # GIVEN a populated store

    # WHEN trying to retrieve a tag with None as name
    tag_query: Query = apply_tag_filter(
        tags=populated_store._get_query(table=Tag),
        filter_functions=[TagFilter.BY_NAME],
    )
    assert isinstance(tag_query, Query)

    # THEN the retrieved query is empty
    assert tag_query.count() == 0
