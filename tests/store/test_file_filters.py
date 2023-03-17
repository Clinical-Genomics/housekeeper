from sqlalchemy.orm import Query

from housekeeper.store import Store
from housekeeper.store.models import File
from housekeeper.store.filters.file_filters import filter_files_by_id


def test_filter_files_by_id_returns_the_correct_file(populated_store: Store):
    """Test getting collaboration by internal_id."""

    # GIVEN a store with a file
    file: File = populated_store._get_file_query().first()
    assert file

    # WHEN retrieving the file by id
    file_query: Query = filter_files_by_id(
        files=populated_store._get_file_query(),
        file_id=file.id,
    )

    # THEN a query should be returned
    assert isinstance(file_query, Query)

    # THEN a file should be returned
    filtered_file: File = file_query.first()
    assert isinstance(filtered_file, File)

    # THEN the id should match
    assert filtered_file.id == file.id
