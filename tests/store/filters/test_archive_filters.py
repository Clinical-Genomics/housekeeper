from sqlalchemy.orm import Query

from housekeeper.store import Store
from housekeeper.store.filters.archive_filters import (
    filter_archiving_ongoing,
    filter_retrieval_ongoing,
    filter_by_archiving_task_id,
    filter_by_retrieval_task_id,
)
from housekeeper.store.models import Archive


def test_filter_archiving_ongoing(populated_store: Store, archiving_task_id: int):
    """Tests filtering of Archives on if their archiving task is finished."""
    # GIVEN a populated store with, an ongoing task

    # WHEN filtering a query by ongoing archiving
    ongoing_archives: Query = filter_archiving_ongoing(
        archives=populated_store._get_query(table=Archive)
    )

    # THEN the archive with the ongoing archiving task should be returned
    assert ongoing_archives.count() > 0
    for archive in ongoing_archives:
        assert archive.archiving_task_id
        assert not archive.archived_at


def test_filter_retrieval_ongoing(archive: Archive, populated_store: Store, retrieval_task_id: int):
    """Tests filtering of Archives on if their retrieval task is finished."""
    # GIVEN a populated store with and an ongoing task
    archive.retrieved_at = None
    archive.retrieval_task_id = retrieval_task_id

    # WHEN filtering a query by ongoing retrieval
    ongoing_archives: Query = filter_retrieval_ongoing(
        archives=populated_store._get_query(table=Archive)
    )
    # THEN the archive with the ongoing retrieval task should be returned
    assert ongoing_archives.count() > 0
    for archive in ongoing_archives:
        assert archive.retrieval_task_id
        assert not archive.retrieved_at


def test_filter_by_archiving_task_id(archiving_task_id: int, populated_store: Store):
    """Tests the filtering of archives by archiving task id."""
    # GIVEN a store with an archive with the given archiving task id

    # WHEN filtering by archiving task id
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
    """Tests the filtering of archives by retrieval task id."""
    # GIVEN a store with an archive with the given retrieval task id
    archive.retrieval_task_id = retrieval_task_id

    # WHEN filtering by retrieval task id
    archives_with_given_task_id: Query = filter_by_retrieval_task_id(
        archives=populated_store._get_query(table=Archive), task_id=retrieval_task_id
    )

    # THEN only one with matching retrieval task id should be returned
    assert archives_with_given_task_id.count() > 0
    for archive in archives_with_given_task_id:
        assert archive.retrieval_task_id == retrieval_task_id
