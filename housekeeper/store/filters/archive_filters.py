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


class ArchiveFilter(Enum):
    """Define Tag filter functions."""

    FILTER_ARCHIVING_IN_PROGRESS: Callable = filter_archiving_in_progress
    FILTER_RETRIEVAL_IN_PROGRESS: Callable = filter_retrieval_in_progress


def apply_archive_filter(
    archives: Query,
    filter_functions: List[Callable],
) -> Query:
    """Apply filtering functions to archive and return filtered Query."""
    for filter_function in filter_functions:
        archives: Query = filter_function(archives=archives)
    return archives
