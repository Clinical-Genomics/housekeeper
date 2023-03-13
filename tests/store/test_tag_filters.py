from housekeeper.store import Store
from housekeeper.store.models import Tag
from housekeeper.store.tag_filters import filter_tag_by_name
from sqlalchemy.orm import Query
from typing import List


def test_filter_tag_by_name_returns_correct_tag(populated_store: Store, sample_tag_name: str):
    """Test that fetching a tag by name returns a tag with the expected name."""

    # GIVEN a store with the desired tag
    tags: Query = populated_store._get_tag_query()
    tag_names: List[str] = [t.name for t in tags.all()]
    assert sample_tag_name in tag_names

    # WHEN retrieving the tag by name
    tag: Tag = filter_tag_by_name(
        tags=tags,
        tag_name=sample_tag_name,
    ).first()

    # THEN a tag should be returned
    assert isinstance(tag, Tag)

    # THEN the name should match
    assert tag.name == sample_tag_name
