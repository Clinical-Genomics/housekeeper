from housekeeper.store import Store
from housekeeper.store.models import Tag
from housekeeper.store.tag_filters import filter_tag_by_name


def test_filter_tag_by_id_returns_the_correct_tag(populated_store: Store):
    """Test getting collaboration by internal_id."""

    # GIVEN a store with a tag
    tag: Tag = populated_store.session.query(Tag).first()
    assert tag

    tag_name: str = tag.name

    # WHEN retrieving the tag by name
    tag: Tag = filter_tag_by_name(
        tags=populated_store._get_tag_query(),
        tag_name=tag_name,
    ).first()

    # THEN a tag should be returned
    assert isinstance(tag, Tag)

    # THEN the name should match
    assert tag.name == tag_name
