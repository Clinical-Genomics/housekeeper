from datetime import datetime
from enum import Enum
from typing import Callable

from sqlalchemy.orm import Query

from housekeeper.store.models import Version


def filter_version_by_id(versions: Query, version_id: int, **kwargs) -> Query:
    """Return version by version id."""
    return versions.filter(Version.id == version_id)


def filter_version_by_date(versions: Query, before_date: datetime, **kwargs) -> Query:
    """Return version by date."""
    return versions.filter(Version.created_at < before_date)


class VersionFilter(Enum):
    """Define Version filter functions."""

    BY_ID: Callable = filter_version_by_id
    BY_DATE: Callable = filter_version_by_date


def apply_version_filter(
    versions: Query,
    filter_functions: list[Callable],
    version_id: int | None = None,
    before_date: datetime | None = None,
) -> Query:
    """Apply filtering functions and return filtered query."""
    for filter_function in filter_functions:
        versions: Query = filter_function(
            versions=versions, version_id=version_id, before_date=before_date
        )
    return versions
