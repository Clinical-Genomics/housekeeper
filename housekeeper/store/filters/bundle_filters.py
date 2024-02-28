from enum import Enum
from typing import Callable

from sqlalchemy.orm import Query

from housekeeper.store.models import Bundle


def filter_bundle_by_name(bundles: Query, bundle_name: str, **kwargs) -> Query:
    """Return bundle by bundle name."""
    return bundles.filter(Bundle.name == bundle_name)


def filter_bundle_by_id(bundles: Query, bundle_id: int, **kwargs) -> Query:
    """Return bundle by bundle id."""
    return bundles.filter(Bundle.id == bundle_id)


class BundleFilters(Enum):
    """Define Bundle filter functions."""

    BY_NAME: Callable = filter_bundle_by_name
    BY_ID: Callable = filter_bundle_by_id


def apply_bundle_filter(
    bundles: Query,
    filter_functions: list[Callable],
    bundle_name: str | None = None,
    bundle_id: int | None = None,
) -> Query:
    """Apply filtering functions and return filtered query."""
    for filter_function in filter_functions:
        bundles: Query = filter_function(
            bundles=bundles,
            bundle_name=bundle_name,
            bundle_id=bundle_id,
        )
    return bundles
