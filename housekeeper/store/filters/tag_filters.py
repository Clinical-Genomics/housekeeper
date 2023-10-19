from enum import Enum
from typing import Callable, Optional

from sqlalchemy.orm import Query

from housekeeper.store.models import Tag


def filter_tag_by_name(tags: Query, tag_name: str) -> Query:
    """Return tag by bundle name."""
    return tags.filter(Tag.name == tag_name)


class TagFilter(Enum):
    """Define Tag filter functions."""

    FILTER_BY_NAME: Callable = filter_tag_by_name


def apply_tag_filter(
    tags: Query,
    filter_functions: list[Callable],
    tag_name: Optional[str] = None,
) -> Query:
    """Apply filtering functions to tag and return filtered Query."""
    for filter_function in filter_functions:
        tags: Query = filter_function(
            tags=tags,
            tag_name=tag_name,
        )
    return tags
