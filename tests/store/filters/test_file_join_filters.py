from typing import List

from sqlalchemy.orm import Query

from housekeeper.store.api.core import Store
from housekeeper.store.filters.file_filters import (
    filter_files_by_tags,
    filter_files_by_is_archived,
)
from housekeeper.store.models import File


def test_filter_files_by_tags_returns_correct_files(populated_store: Store):
    """Test filtering files by tags."""

    # GIVEN a store with files
    file: File = populated_store._get_query(table=File).first()
    tag_names: List[str] = [tag.name for tag in file.tags]

    # WHEN filtering files by tags
    filtered_files_query = filter_files_by_tags(
        files=populated_store._get_join_file_tag_query(),
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
    # GIVEN a tag that does not exist in any files in the store
    tag_name = "nonexistent_tag"

    # WHEN filtering files by the nonexistent tag
    filtered_files_query = filter_files_by_tags(
        files=populated_store._get_join_file_tag_query(),
        tag_names=[tag_name],
    )

    # THEN the filtered files list should be empty
    assert len(filtered_files_query.all()) == 0


def test_filter_files_by_archive_true(populated_store: Store):
    """Tests the filtering for archived files."""

    # GIVEN as store with files

    # WHEN filtering on archived files
    archived_files_query: Query = filter_files_by_is_archived(
        files=populated_store._get_join_file_tags_archive_query(),
        is_archived=True,
    )

    # THEN all files returned should have an archive object linked to it
    for file in archived_files_query:
        assert file.archive


def test_filter_files_by_archive_false(populated_store: Store):
    """Tests the filtering for non-archived files."""

    # GIVEN as store with files

    # WHEN filtering on non-archived files
    archived_files_query: Query = filter_files_by_is_archived(
        files=populated_store._get_join_file_tags_archive_query(),
        is_archived=False,
    )

    # THEN none of the files returned should have an archive object linked to it
    for file in archived_files_query:
        assert file.archive is None
