from housekeeper.store import Store
from housekeeper.store.models import Tag
from housekeeper.store.tag_filters import filter_tag_by_name
from sqlalchemy.orm import Query


def test_filter_tag_by_name_returns_correct_tag(populated_store: Store, sample_tag_name: str):
    """Test that fetching a tag by name returns a tag with the expected name."""

    # GIVEN a store with tags
    tags: Query = populated_store._get_tag_query()
    # tag: Tag = populated_store.session.query(Tag).first()
    assert tags.count() > 0

    # WHEN retrieving the tag by name
    tag: Tag = filter_tag_by_name(
        tags=tags,
        tag_name=sample_tag_name,
    ).first()

    # THEN a tag should be returned
    assert isinstance(tag, Tag)

    # THEN the name should match
    assert tag.name == sample_tag_name
