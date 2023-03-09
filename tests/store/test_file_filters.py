
from typing import List
from housekeeper.store import Store
from housekeeper.store.models import File
from housekeeper.store.filters.file_filters import filter_files_by_id


def test_filter_files_by_id_returns_the_correct_file(populated_store: Store):
    """Test getting collaboration by internal_id."""

    # GIVEN a store with a file
    file: File = populated_store.session.query(File).first()
    assert file

    file_id: int = file.id

    # WHEN retrieving the file by id
    file: File = filter_files_by_id(
        files=populated_store._get_file_query(),
        file_id=file_id,
    ).first()

    # THEN a file should be returned
    assert isinstance(file, File)

    # THEN the id should match
    assert file.id == file_id
