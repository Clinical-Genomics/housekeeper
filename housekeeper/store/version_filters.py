from enum import Enum
from typing import Callable, List, Optional
from sqlalchemy.orm import Query
from housekeeper.store.models import Version


def filter_version_by_id(versions: Query, version_id: int, **kwargs) -> Query:
    """Return version by version id."""
    return versions.filter(Version.id == version_id)


class VersionFilters(Enum):
    """Define Version filter functions."""
    FILTER_BY_ID: Callable = filter_version_by_id


def apply_version_filter(
    versions: Query,
    filter_functions: List[Callable],
    version_id: Optional[int] = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for filter_function in filter_functions:
        versions: Query = filter_function(
            versions=versions,
            version_id=version_id,
        )
    return versions
