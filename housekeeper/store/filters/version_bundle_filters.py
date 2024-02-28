import datetime as dt
from enum import Enum
from typing import Callable

from sqlalchemy.orm import Query

from housekeeper.store.models import Bundle, Version


def filter_version_by_name_and_bundle_date(
    version_bundles: Query, bundle_name: str, version_date: dt.datetime, **kwargs
) -> Query:
    """Return version by date and bundle name."""
    return version_bundles.filter(Bundle.name == bundle_name, Version.created_at == version_date)


class VersionBundleFilters(Enum):
    """Define Version filter functions."""

    BY_DATE_AND_NAME: Callable = filter_version_by_name_and_bundle_date


def apply_version_bundle_filter(
    version_bundles: Query,
    filter_functions: list[Callable],
    bundle_name: str | None = None,
    version_date: dt.datetime | None = None,
) -> Query:
    """Apply filtering functions and return filtered query."""
    for filter_function in filter_functions:
        version_bundles: Query = filter_function(
            version_bundles=version_bundles,
            bundle_name=bundle_name,
            version_date=version_date,
        )
    return version_bundles
