import pytest
from sqlalchemy.orm import Query

from housekeeper.store.filters.file_filters import (
    filter_files_by_id,
    filter_files_by_is_archived,
    filter_files_by_path,
    filter_files_by_tags,
)
from housekeeper.store.models import File
from housekeeper.store.store import Store


def test_filter_files_by_id_returns_query(populated_store: Store):
    """Test that filter_files_by_id returns a Query object."""

    # GIVEN a store with a file
    file: File = populated_store._get_query(table=File).first()
    assert file

    # WHEN retrieving the file by id
    file_query: Query = filter_files_by_id(
        files=populated_store._get_query(table=File), file_id=file.id
    )

    # THEN a query should be returned
    assert isinstance(file_query, Query)


def test_filter_files_by_id_returns_the_correct_file(populated_store: Store):
    """Test filtering files by id returns the correct file."""

    # GIVEN a store with a file
    file: File = populated_store._get_query(table=File).first()
    assert file

    # WHEN retrieving the file by id
    file_query: Query = filter_files_by_id(
        files=populated_store._get_query(table=File),
        file_id=file.id,
    )

    # THEN a file should be returned
    filtered_file: File = file_query.first()
    assert isinstance(filtered_file, File)

    # THEN the id should match
    assert filtered_file.id == file.id


def test_filter_files_by_path_returns_the_correct_file(populated_store: Store):
    """ "Test filtering files by path returns the correct file."""
    # GIVEN a store with some files
    files = populated_store._get_query(table=File)

    file: File = files.first()
    assert file

    # WHEN retrieving the file by path
    file_query: Query = filter_files_by_path(
        files=files,
        file_path=file.path,
    )

    # THEN a file should be returned
    filtered_file: File = file_query.first()
    assert isinstance(filtered_file, File)

    # THEN the path should match
    assert filtered_file.path == file.path


@pytest.mark.parametrize("file_id", [-1, None, "non-existent"])
def test_filter_files_by_id_returns_none_for_invalid_id(populated_store: Store, file_id):
    """Test that filter_files_by_id returns None for invalid file ids."""

    # WHEN retrieving the file by an invalid id
    file_query: Query = filter_files_by_id(
        files=populated_store._get_query(table=File), file_id=file_id
    )

    # THEN no file should be returned
    filtered_file: File = file_query.first()
    assert filtered_file is None


def test_filter_files_by_tags_returns_correct_files(populated_store: Store):
    """Test filtering files by tags."""

    # GIVEN a store with files
    file: File = populated_store._get_query(table=File).first()
    tag_names: list[str] = [tag.name for tag in file.tags]

    # WHEN filtering files by tags
    filtered_files_query = filter_files_by_tags(
        files=populated_store._get_join_file_tag_query(),
        tag_names=tag_names,
    )

    filtered_files: list[File] = filtered_files_query.all()

    # THEN each file should have all the requested tags
    for filtered_file in filtered_files:
        assert all(tag.name in tag_names for tag in filtered_file.tags)


def test_filter_files_by_tags_returns_empty_list_when_no_files_match_tags(
    populated_store: Store,
):
    """Test filtering files by tags when no files match the given tags."""

    # GIVEN a store with files
    # GIVEN a tag that does not exist in any files in the store
    tag_name = "non_existent_tag"

    # WHEN filtering files by the non_existent tag
    filtered_files_query = filter_files_by_tags(
        files=populated_store._get_join_file_tag_query(),
        tag_names=[tag_name],
    )

    # THEN the filtered files list should be empty
    assert len(filtered_files_query.all()) == 0


def test_filter_files_by_archive_true(populated_store: Store):
    """Tests the filtering for archived files."""

    # GIVEN as store with files

    # WHEN filtering by archived files
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
    non_archived_files_query: Query = filter_files_by_is_archived(
        files=populated_store._get_join_file_tags_archive_query(),
        is_archived=False,
    )

    # THEN none of the files returned should have an archive object linked to it
    for file in non_archived_files_query:
        assert file.archive is None
