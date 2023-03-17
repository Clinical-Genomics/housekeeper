from enum import Enum
from typing import Callable, List, Optional
from sqlalchemy.orm import Query
from sqlalchemy import func as sqlalchemy_func

from housekeeper.store.models import File, Tag


def filter_files_by_tags(files_tags: Query, tags: List[str], **kwargs) -> Query:
    """Filter files by tags."""
    return files_tags.filter(Tag.name.in_(tags)).group_by(File.id).having(sqlalchemy_func.count(Tag.name) == len(tags))

class FileTagFilter(Enum):
    """Define File Tag filter functions."""
    FILTER_FILES_BY_TAGS: Callable = filter_files_by_tags


def apply_file_tag_filter(
    files_tags: Query,
    filter_functions: List[Callable],
    tags: Optional[List[str]] = None,
) -> Query:
    """Apply filtering functions and return filtered query."""
    for filter_function in filter_functions:
        files_tags: Query = filter_function(
            files_tags=files_tags,
            tags=tags
        )
    return files_tags
