from enum import Enum
from typing import Callable, List, Optional
from sqlalchemy.orm import Query
from sqlalchemy import func as sqlalchemy_func

from housekeeper.store.models import File, Tag


def filter_files_by_tags(files: Query, tag_names: List[str], **kwargs) -> Query:
    """Filter files by tag names."""
    return (
        files.filter(Tag.name.in_(tag_names))
        .group_by(File.id)
        .having(sqlalchemy_func.count(Tag.name) == len(tag_names))
    )


def filter_files_by_archive(files: Query, is_archived: bool, **kwargs) -> Query:
    """Filters the query depending on if the files are archived or not."""
    return files.filter((File.archive != None) == is_archived)


class FileJoinFilter(Enum):
    """Define filter functions for joins between File and other tables."""

    FILTER_FILES_BY_TAGS: Callable = filter_files_by_tags
    FILTER_FILES_BY_ARCHIVE: Callable = filter_files_by_archive


def apply_file_filter_extended(
    files: Query,
    filter_functions: List[Callable],
    is_archived: Optional[bool] = None,
    tag_names: Optional[List[str]] = None,
) -> Query:
    """Apply filtering functions and return filtered query."""
    for filter_function in filter_functions:
        files: Query = filter_function(
            files=files, is_archived=is_archived, tag_names=tag_names
        )
    return files
