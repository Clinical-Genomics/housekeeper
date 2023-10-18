from enum import Enum
from typing import Callable, Optional

from sqlalchemy import func as sqlalchemy_func
from sqlalchemy.orm import Query

from housekeeper.store.models import File, Tag


def filter_files_by_id(files: Query, file_id: int, **kwargs) -> Query:
    """Filter files by file id."""
    return files.filter(File.id == file_id)


def filter_files_by_path(files: Query, file_path: str, **kwargs) -> Query:
    """Filter files by path."""
    return files.filter(File.path == file_path)


def filter_files_by_tags(files: Query, tag_names: list[str], **kwargs) -> Query:
    """Filter files by tag names."""
    return (
        files.filter(Tag.name.in_(tag_names))
        .group_by(File.id)
        .having(sqlalchemy_func.count(Tag.name) == len(tag_names))
    )


def filter_files_by_is_archived(files: Query, is_archived: bool, **kwargs) -> Query:
    """Filters the query depending on if the files are archived or not."""
    return files.filter((File.archive != None) == is_archived)


class FileFilter(Enum):
    """Define filter functions for Files joined tables."""

    FILTER_BY_ID: Callable = filter_files_by_id
    FILTER_BY_PATH: Callable = filter_files_by_path
    FILTER_FILES_BY_TAGS: Callable = filter_files_by_tags
    FILTER_FILES_BY_IS_ARCHIVED: Callable = filter_files_by_is_archived


def apply_file_filter(
    files: Query,
    filter_functions: list[Callable],
    file_id: Optional[int] = None,
    file_path: Optional[str] = None,
    is_archived: Optional[bool] = None,
    tag_names: Optional[list[str]] = None,
) -> Query:
    """Apply filtering functions and return filtered query."""
    for filter_function in filter_functions:
        files: Query = filter_function(
            files=files,
            file_id=file_id,
            file_path=file_path,
            is_archived=is_archived,
            tag_names=tag_names,
        )
    return files
