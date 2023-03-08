from enum import Enum
from typing import Callable, List, Optional
from sqlalchemy.orm import Query
from sqlalchemy import func as sqlalchemy_func

from housekeeper.store.models import File, Tag


def filter_files_by_id(files: Query, file_id: int, **kwargs) -> Query:
    """Filter files by file id."""
    return files.filter(File.id == file_id)


def filter_files_by_tags(files: Query, tags: List[str], **kwargs) -> Query:
    """Filter files by tags."""
    files_tags = files.join(File.tags)
    return files_tags.filter(Tag.name.in_(tags)).group_by(File.id).having(sqlalchemy_func.count(Tag.name) == len(tags))

class FileFilters(Enum):
    """Define File filter functions."""
    FILTER_BY_ID: Callable = filter_files_by_id
    FILTER_BY_TAGS: Callable = filter_files_by_tags


def apply_file_filters(
    files: Query,
    filter_functions: List[Callable],
    file_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for filter_function in filter_functions:
        files: Query = filter_function(
            files=files,
            file_id=file_id,
            tags=tags
        )
    return files
