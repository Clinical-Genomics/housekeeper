from datetime import datetime
from enum import Enum
from typing import Callable

from sqlalchemy import and_
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import BooleanClauseList

from housekeeper.store.models import Archive

ARCHIVING_ONGOING: BooleanClauseList = and_(Archive.archiving_task_id, Archive.archived_at == None)
RETRIEVAL_ONGOING: BooleanClauseList = and_(Archive.retrieval_task_id, Archive.retrieved_at == None)


def filter_archiving_ongoing(archives: Query, **kwargs) -> Query:
    """Return archives where the archiving is not marked as completed."""
    return archives.filter(ARCHIVING_ONGOING)


def filter_retrieval_ongoing(archives: Query, **kwargs) -> Query:
    """Return archives where the retrieval is not marked as completed."""
    return archives.filter(RETRIEVAL_ONGOING)


def filter_by_archiving_task_id(archives: Query, task_id: int, **kwargs) -> Query:
    """Return archives where the archiving task id matches the one given."""
    return archives.filter(Archive.archiving_task_id == task_id)


def filter_by_retrieval_task_id(archives: Query, task_id: int, **kwargs) -> Query:
    """Return archives where the retrieval task id matches the one given."""
    return archives.filter(Archive.retrieval_task_id == task_id)


def filter_by_retrieved_before(archives: Query, retrieved_before: datetime, **kwargs) -> Query:
    """Returns archives which were retrieved before the given date."""
    return archives.filter(Archive.retrieved_at < retrieved_before)


class ArchiveFilter(Enum):
    """Define Archive filter functions."""

    ARCHIVING_ONGOING: Callable = filter_archiving_ongoing
    RETRIEVAL_ONGOING: Callable = filter_retrieval_ongoing
    BY_ARCHIVING_TASK_ID: Callable = filter_by_archiving_task_id
    BY_RETRIEVAL_TASK_ID: Callable = filter_by_retrieval_task_id
    BY_RETRIEVED_BEFORE: Callable = filter_by_retrieved_before


def apply_archive_filter(
    archives: Query,
    filter_functions: list[ArchiveFilter],
    task_id: int = None,
    retrieved_before: datetime = None,
) -> Query:
    """Apply filtering functions to archives and return filtered Query."""
    for filter_function in filter_functions:
        archives: Query = filter_function(
            archives=archives, task_id=task_id, retrieved_before=retrieved_before
        )
    return archives
