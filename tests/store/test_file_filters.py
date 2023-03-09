
from typing import List
from housekeeper.store import Store
from housekeeper.store.models import File
from housekeeper.store.file_filters import filter_files_by_id, filter_files_by_tags


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

def test_filter_files_by_tags_returns_correct_files(populated_store: Store):
    """Test filtering files by tags."""

    # GIVEN a store with files
    file: File = populated_store._get_file_query().first()
    tag_names: List[str] = [tag.name for tag in file.tags]

    # WHEN filtering files by tags
    filtered_files_query = filter_files_by_tags(
        files=populated_store._get_file_query(),
        tags=tag_names,
    )

    filtered_files: List[File] = filtered_files_query.all()

    # THEN each file should have all the requested tags
    for file in filtered_files:
        assert all(
            tag.name in tag_names for tag in file.tags
        )
