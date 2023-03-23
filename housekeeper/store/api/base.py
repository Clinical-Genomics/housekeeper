"""This module defines a BaseHandler class holding different models"""

from typing import Type
from housekeeper.store.models import Bundle, File, Version, Tag
from alchy import ModelBase, Query


class BaseHandler:
    """This is a base class holding different models"""

    Bundle: Type[ModelBase] = Bundle
    Version: Type[ModelBase] = Version
    File: Type[ModelBase] = File
    Tag: Type[ModelBase] = Tag

    @staticmethod
    def _get_query(table: Type[ModelBase]) -> Query:
        """Return a query for the given table."""
        return table.query

    def _get_join_version_bundle_query(self) -> Query:
        """Return version bundle query."""
        return self.Version.query.join(Version.bundle)

    def _get_join_file_tag_query(self) -> Query:
        """Return file tag query."""
        return self.File.query.join(File.tags)

    def _get_join_version_query(self, query: Query):
        return query.join(Version)
