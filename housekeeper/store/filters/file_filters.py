from enum import Enum
from typing import Callable, List, Optional
from sqlalchemy.orm import Query

from housekeeper.store.models import File


def filter_files_by_id(files: Query, file_id: int, **kwargs) -> Query:
    """Filter files by file id."""
    return files.filter(File.id == file_id)


class FileFilters(Enum):
    """Define File filter functions."""
    FILTER_BY_ID: Callable = filter_files_by_id


def apply_file_filters(
    files: Query,
    filter_functions: List[Callable],
    file_id: Optional[int] = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for filter_function in filter_functions:
        files: Query = filter_function(
            files=files,
            file_id=file_id,
        )
    return files