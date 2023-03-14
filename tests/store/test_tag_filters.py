from housekeeper.store import Store
from housekeeper.store.models import Tag
from housekeeper.store.tag_filters import filter_tag_by_name, TagFilter, apply_tag_filter
from sqlalchemy.orm import Query
from typing import List


def test_filter_tag_by_name_returns_correct_tag(populated_store: Store, sample_tag_name: str):
    """Test that fetching a tag by name returns a tag with the expected name."""

    # GIVEN a store with the desired tag
    all_tags: Query = populated_store._get_tag_query()
    all_tag_names: List[str] = [t.name for t in all_tags.all()]
    assert sample_tag_name in all_tag_names

    # WHEN retrieving the tag by name
    tag: Tag = filter_tag_by_name(
        tags=all_tags,
        tag_name=sample_tag_name,
    ).first()

    # THEN a tag should be returned
    assert isinstance(tag, Tag)

    # THEN the name should match
    assert tag.name == sample_tag_name


def test_filter_tag_by_name_non_existent_tag(populated_store: Store, non_existent_tag_name):
    """Test that using a non-existent tag name returns an empty query."""
    # GIVEN a tag name not included in a populated store
    all_tags: Query = populated_store._get_tag_query()
    all_tag_names: List[str] = [t.name for t in all_tags.all()]
    assert non_existent_tag_name not in all_tag_names

    # WHEN retrieving the tag by name
    tags: Query = filter_tag_by_name(
        tags=all_tags,
        tag_name=non_existent_tag_name,
    )

    # THEN the retrieved query is empty
    assert tags.count() == 0


def test_filter_tag_by_name_with_none_tag_name(populated_store: Store):
    """Test that using None as tag name argument returns an empty query."""
    # GIVEN a populated store

    # WHEN trying to retrieve a tag with None as name
    tags: Query = filter_tag_by_name(
        tags=populated_store._get_tag_query(),
        tag_name=None,
    )

    # THEN the retrieved query is empty
    assert tags.count() == 0


def test_apply_tag_filter_without_tag_name(populated_store: Store):
    """Test that omitting the tag name argument returns an empty query"""
    # GIVEN a populated store

    # WHEN trying to retrieve a tag with None as name
    tags: Query = apply_tag_filter(
        tags=populated_store._get_tag_query(),
        filter_functions=[TagFilter.FILTER_BY_NAME],
    )

    # THEN the retrieved query is empty
    assert tags.count() == 0
