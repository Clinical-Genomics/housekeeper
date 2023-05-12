from sqlalchemy.orm import Query

from housekeeper.store import Store
from housekeeper.store.filters.archive_filters import (
    filter_archiving_in_progress,
    filter_retrieval_in_progress,
    filter_by_archiving_task_id,
    filter_by_retrieval_task_id,
)
from housekeeper.store.models import Archive


def test_filter_archiving_in_progress(populated_store: Store, archiving_task_id: int):
    """Tests filtering Archives on if their archiving task is finished."""
    # GIVEN a populated store with, an unfinished task

    # WHEN filtering a query in unfinished tasks
    archives_in_progress: Query = filter_archiving_in_progress(
        archives=populated_store._get_query(table=Archive)
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
    archives_in_progress: Query = filter_retrieval_in_progress(
        archives=populated_store._get_query(table=Archive)
    )
    # THEN the unfinished task should be returned
    assert archives_in_progress.count() > 0
    for archive in archives_in_progress:
        assert archive.retrieval_task_id
        assert not archive.retrieved_at


def test_filter_by_archiving_task_id(archiving_task_id: int, populated_store: Store):
    """Tests the filtering archives by archiving task id."""
    # GIVEN a store with an archive with the given archiving_task_id

    # WHEN filtering on archiving tasks
    archives_with_given_task_id: Query = filter_by_archiving_task_id(
        archives=populated_store._get_query(table=Archive), task_id=archiving_task_id
    )

    # THEN only one with matching archiving task id should be returned
    assert archives_with_given_task_id.count() > 0
    for archive in archives_with_given_task_id:
        assert archive.archiving_task_id == archiving_task_id


def test_filter_by_retrival_task_id(
    archive: Archive, retrieval_task_id: int, populated_store: Store
):
    """Tests the filtering archives by retrievaltask id."""
    # GIVEN a store with an archive with the given archiving_task_id
    archive.retrieval_task_id = retrieval_task_id

    # WHEN filtering on archiving tasks
    archives_with_given_task_id: Query = filter_by_retrieval_task_id(
        archives=populated_store._get_query(table=Archive), task_id=retrieval_task_id
    )

    # THEN only one with matching archiving task id should be returned
    assert archives_with_given_task_id.count() > 0
    for archive in archives_with_given_task_id:
        assert archive.retrieval_task_id == retrieval_task_id
