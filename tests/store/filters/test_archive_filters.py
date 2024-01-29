import datetime

import pytest
from sqlalchemy.orm import Query

from housekeeper.store.filters.archive_filters import (
    filter_archiving_ongoing,
    filter_by_archiving_task_id,
    filter_by_retrieval_task_id,
    filter_by_retrieved_before,
    filter_retrieval_ongoing,
)
from housekeeper.store.models import Archive
from housekeeper.store.store import Store


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


def test_filter_by_retrieval_task_id(
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


@pytest.mark.parametrize(
    "retrieved_at, expected_result",
    [
        (datetime.datetime(year=2023, month=12, day=12), False),
        (datetime.datetime(year=2023, month=1, day=1), True),
    ],
)
def test_filter_by_retrieved_before(
    archive: Archive,
    retrieval_task_id: int,
    populated_store: Store,
    retrieved_at: datetime,
    expected_result: bool,
):
    """Tests filtering archives on only those retrieved before a given date."""
    # GIVEN a store with an archive with the given retrieval task id and which was retrieved at the given time
    archive.retrieval_task_id = retrieval_task_id
    archive.retrieved_at = retrieved_at

    # GIVEN that we want only files that were retrieved before 2023-06-06
    retrieved_before: datetime = datetime.datetime(year=2023, month=6, day=6)

    # WHEN filtering by when it was retrieved
    archives_retrieved_before_date: list[Archive] = filter_by_retrieved_before(
        archives=populated_store._get_query(table=Archive), retrieved_before=retrieved_before
    ).all()

    # THEN the archive is only returned if it was retrieved before date
    assert (archive in archives_retrieved_before_date) == expected_result
