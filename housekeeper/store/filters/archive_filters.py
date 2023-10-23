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


class ArchiveFilter(Enum):
    """Define Archive filter functions."""

    FILTER_ARCHIVING_ONGOING: Callable = filter_archiving_ongoing
    FILTER_RETRIEVAL_ONGOING: Callable = filter_retrieval_ongoing
    FILTER_BY_ARCHIVING_TASK_ID: Callable = filter_by_archiving_task_id
    FILTER_BY_RETRIEVAL_TASK_ID: Callable = filter_by_retrieval_task_id


def apply_archive_filter(
    archives: Query, filter_functions: list[ArchiveFilter], task_id: int = None
) -> Query:
    """Apply filtering functions to archives and return filtered Query."""
    for filter_function in filter_functions:
        archives: Query = filter_function(archives=archives, task_id=task_id)
    return archives
