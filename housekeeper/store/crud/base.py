"""This module defines a BaseHandler class holding different models"""

from typing import Type

from sqlalchemy.orm import Query, Session

from housekeeper.store.models import File, Model, Version


class BaseHandler:
    """This is a base class holding different models."""

    def __init__(self, session: Session):
        self.session = session

    def _get_query(self, table: Type[Model]) -> Query:
        """Return a query for the given table."""
        return self.session.query(table)

    def _get_join_version_bundle_query(self) -> Query:
        """Return version bundle query."""
        return self._get_query(table=Version).join(Version.bundle)

    def _get_join_file_tag_query(self) -> Query:
        """Return file tag query."""
        return self._get_query(table=File).join(File.tags)

    def _get_join_version_query(self, query: Query):
        """Joins the given query with the version table."""
        return query.join(Version)

    def _get_join_bundle_to_file_query(self, file_query: Query) -> Query:
        """Joins bundle information to a File query."""
        return file_query.join(File.version).join(Version.bundle)

    def _get_join_file_tags_archive_query(self) -> Query:
        """Returns a File query joined with bundle, tags and archive information."""
        return self._get_join_bundle_to_file_query(
            file_query=self._get_join_file_tag_query()
        ).outerjoin(File.archive)
