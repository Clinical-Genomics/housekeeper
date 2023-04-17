import pytest
from sqlalchemy.orm import Query

from housekeeper.store import Store
from housekeeper.store.models import File
from housekeeper.store.filters.file_filters import (
    filter_files_by_id,
    filter_files_by_path,
)


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
def test_filter_files_by_id_returns_none_for_invalid_id(
    populated_store: Store, file_id
):
    """Test that filter_files_by_id returns None for invalid file ids."""

    # WHEN retrieving the file by an invalid id
    file_query: Query = filter_files_by_id(
        files=populated_store._get_query(table=File), file_id=file_id
    )

    # THEN no file should be returned
    filtered_file: File = file_query.first()
    assert filtered_file is None
