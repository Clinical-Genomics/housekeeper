from typing import List
from housekeeper.store.api.core import Store
from housekeeper.store.filters.file_tags_filters import filter_files_by_tags
from housekeeper.store.models import File


def test_filter_files_by_tags_returns_correct_files(populated_store: Store):
    """Test filtering files by tags."""

    # GIVEN a store with files
    file: File = populated_store._get_query(table=File).first()
    tag_names: List[str] = [tag.name for tag in file.tags]

    # WHEN filtering files by tags
    filtered_files_query = filter_files_by_tags(
        files_tags=populated_store._get_join_file_tag_query(),
        tag_names=tag_names,
    )

    filtered_files: List[File] = filtered_files_query.all()

    # THEN each file should have all the requested tags
    for filtered_file in filtered_files:
        assert all(tag.name in tag_names for tag in filtered_file.tags)


def test_filter_files_by_tags_returns_empty_list_when_no_files_match_tags(
    populated_store: Store,
):
    """Test filtering files by tags when no files match the given tags."""

    # GIVEN a store with files
    # create a tag that does not exist in any files in the store
    tag_name = "nonexistent_tag"

    # WHEN filtering files by the nonexistent tag
    filtered_files_query = filter_files_by_tags(
        files_tags=populated_store._get_join_file_tag_query(),
        tag_names=[tag_name],
    )

    # THEN the filtered files list should be empty
    assert len(filtered_files_query.all()) == 0
