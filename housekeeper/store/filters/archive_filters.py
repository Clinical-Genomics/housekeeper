from enum import Enum
from typing import Callable, List, Optional

from sqlalchemy import or_, and_
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import BooleanClauseList

from housekeeper.store.models import Archive

ARCHIVING_NOT_FINISHED: BooleanClauseList = and_(
    Archive.archiving_task_id, Archive.archived_at == None
)
RETRIEVAL_NOT_FINISHED: BooleanClauseList = and_(
    Archive.retrieval_task_id, Archive.retrieved_at == None
)


def filter_archiving_in_progress(archives: Query) -> Query:
    """Return archives where the archiving is not marked as completed."""
    return archives.filter(ARCHIVING_NOT_FINISHED)


def filter_retrieval_in_progress(archives: Query) -> Query:
    """Return archives where the retrieval is not marked as completed."""
    return archives.filter(RETRIEVAL_NOT_FINISHED)


def filter_by_archiving_task(archives: Query, task_id: int) -> Query:
    """Return archives where the archiving task id matches the one given."""
    return archives.filter(Archive.archiving_task_id == task_id)


def filter_by_retrieval_task(archives: Query, task_id: int) -> Query:
    """Return archives where the retrieval task id matches the one given."""
    return archives.filter(Archive.retrieval_task_id == task_id)


class ArchiveFilter(Enum):
    """Define Tag filter functions."""

    FILTER_ARCHIVING_IN_PROGRESS: Callable = filter_archiving_in_progress
    FILTER_RETRIEVAL_IN_PROGRESS: Callable = filter_retrieval_in_progress
    FILTER_BY_ARCHIVING_TASK: Callable = filter_by_archiving_task
    FILTER_BY_RETRIEVAL_TASK: Callable = filter_by_retrieval_task


def apply_archive_filter(
    archives: Query, filter_functions: List[Callable], task_id: int = None
) -> Query:
    """Apply filtering functions to archives and return filtered Query."""
    for filter_function in filter_functions:
        archives: Query = filter_function(archives=archives, task_id=task_id)
    return archives
