from enum import Enum
from typing import Callable, List, Optional
from sqlalchemy.orm import Query

from housekeeper.store.models import File


def filter_files_by_id(files: Query, file_id: int, **kwargs) -> Query:
    """Filter files by file id."""
    return files.filter(File.id == file_id)


def filter_files_by_path(files: Query, file_path: str, **kwargs) -> Query:
    """Filter files by path."""
    return files.filter(File.path == file_path)


class FileFilter(Enum):
    """Define File filter functions."""

    FILTER_BY_ID: Callable = filter_files_by_id
    FILTER_BY_PATH: Callable = filter_files_by_path


def apply_file_filter(
    files: Query,
    filter_functions: List[Callable],
    file_id: Optional[int] = None,
    file_path: Optional[str] = None,
) -> Query:
    """Apply filtering functions and return filtered query."""
    for filter_function in filter_functions:
        files: Query = filter_function(
            files=files, file_id=file_id, file_path=file_path
        )
    return files
