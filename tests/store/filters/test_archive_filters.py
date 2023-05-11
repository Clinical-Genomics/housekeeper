from sqlalchemy.orm import Query

from housekeeper.store import Store
from housekeeper.store.filters.archive_filters import (
    apply_archive_filter,
    ArchiveFilter,
)
from housekeeper.store.models import Archive


def test_filter_archiving_in_progress(populated_store: Store, archiving_task_id: int):
    """Tests filtering Archives on if their archiving task is finished."""
    # GIVEN a populated store with, an unfinished task

    # WHEN filtering a query in unfinished tasks
    archives_in_progress: Query = apply_archive_filter(
        archives=populated_store._get_query(table=Archive),
        filter_functions=[ArchiveFilter.FILTER_ARCHIVING_IN_PROGRESS],
    )
    # THEN the unfinished task should be returned
    assert archives_in_progress.count() > 0
    for archive in archives_in_progress:
        assert archive.archiving_task_id
        assert not archive.archived_at


def test_filter_retrieval_in_progress(
    archive: Archive, populated_store: Store, retrieval_task_id: int
):
    """Tests filtering Archives on if their retrieval task is finished."""
    # GIVEN a populated store with, an unfinished task
    archive.retrieved_at = None
    archive.retrieval_task_id = retrieval_task_id

    # WHEN filtering a query in unfinished tasks
    archives_in_progress: Query = apply_archive_filter(
        archives=populated_store._get_query(table=Archive),
        filter_functions=[ArchiveFilter.FILTER_RETRIEVAL_IN_PROGRESS],
    )
    # THEN the unfinished task should be returned
    assert archives_in_progress.count() > 0
    for archive in archives_in_progress:
        assert archive.retrieval_task_id
        assert not archive.retrieved_at
