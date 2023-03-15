"""Tests for finding tags in store."""
from housekeeper.store import Store
from housekeeper.store.models import Tag


def test_tag_with_tag_name(populated_store: Store, sample_tag_name: str):
    """Test fetching a tag from database given a tag name."""
    # GIVEN a populated store and a tag name

    # WHEN retrieving a tag from Store
    test_tag = populated_store.get_tag(tag_name=sample_tag_name)

    # THEN a tag should be returned
    assert isinstance(test_tag, Tag)

    # THEN the tag should have the tag name gotten as parameter
    assert test_tag.name == sample_tag_name


def test_tag_without_tag_name(populated_store: Store):
    """Test fetching a tag from database without specifying a tag name returns None."""
    # GIVEN a populated store

    # WHEN retrieving a tag from Store
    test_tag = populated_store.get_tag()

    # THEN a tag should be returned
    assert test_tag is None
