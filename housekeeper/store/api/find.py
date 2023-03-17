"""
This module handles finding things in the store/database
"""
import datetime as dt
import logging
from pathlib import Path
from typing import List, Set
from sqlalchemy.orm import Query

from housekeeper.store.models import Bundle, File, Tag, Version
from housekeeper.store.filters.file_filters import FileFilter, apply_file_filter
from housekeeper.store.filters.bundle_filters import apply_bundle_filter, BundleFilters
from housekeeper.store.filters.version_filters import apply_version_filter, VersionFilters
from housekeeper.store.filters.version_bundle_filters import apply_version_bundle_filter, VersionBundleFilters
from housekeeper.store.filters.file_tags_filters import FileTagFilter, apply_file_tag_filter
from housekeeper.store.tag_filters import TagFilter, apply_tag_filter

from .base import BaseHandler

LOG = logging.getLogger(__name__)


class FindHandler(BaseHandler):
    """Handler for searching the database"""

    def bundles(self):
        """Fetch bundles."""
        LOG.info("Fetching all bundles")
        return self._get_bundle_query()

    def _get_bundle_query(self) -> Query:
        """Return bundle query."""
        return self.Bundle.query

    def _get_file_query(self) -> Query:
        """Return file query."""
        return self.File.query

    def _get_version_query(self) -> Query:
        """Return version query."""
        return self.Version.query

    def _get_join_version_bundle_query(self) -> Query:
        """Return version bundle query."""
        return self.Version.query.join(Version.bundle)

    def _get_join_file_tag_query(self) -> Query:
        """Return file tag query."""
        return self.File.query.join(File.tags)

    def _get_join_version_query(self, query: Query):
        return query.join(Version)

    def get_bundle_by_id(self, bundle_id: int) -> Bundle:
        """Fetch a bundle by id from the store."""
        LOG.info(f"Fetching bundle with id: {bundle_id}")
        return apply_bundle_filter(
            bundles=self._get_bundle_query(),
            filter_functions=[BundleFilters.FILTER_BY_ID],
            bundle_id=bundle_id,
        ).first()
     
    def get_bundle_by_name(self, bundle_name: str) -> Bundle:
        """Get a bundle by name from the store."""
        LOG.info(f"Fetching bundle with name: {bundle_name}")
        return apply_bundle_filter(
            bundles=self._get_bundle_query(),
            filter_functions=[BundleFilters.FILTER_BY_NAME],
            bundle_name=bundle_name,
        ).first()

    def version(
        self, bundle: str = None, date: dt.datetime = None, version_id: int = None
    ) -> Version:
        """Fetch a version from the store."""
        if version_id:
            LOG.info(f"Fetching version with id: {version_id}")
            return apply_version_filter(
                versions=self._get_version_query(),
                filter_functions=[VersionFilters.FILTER_BY_ID],
                version_id=version_id,
            ).first()

        return apply_version_bundle_filter(
            version_bundles=self._get_join_version_bundle_query(),
            filter_functions=[VersionBundleFilters.FILTER_BY_DATE_AND_NAME],
            version_date=date,
            bundle_name=bundle,
        ).first()

    def get_tag(self, tag_name: str = None) -> Tag:
        """Return a tag from the database."""
        LOG.info(f"Fetching tag with name: {tag_name}")
        return apply_tag_filter(
            tags=self._get_tag_query(),
            filter_functions=[TagFilter.FILTER_BY_NAME],
            tag_name=tag_name,
        ).first()

    def get_tags(self) -> Query:
        """Return all tags from the database."""
        LOG.info("Fetching all tags")
        return self._get_tag_query()

    def _get_tag_query(self) -> Query:
        """Return a tag query."""
        return self.Tag.query

    def get_file_by_id(self, file_id: int):
        """Get a file by record id."""
        return apply_file_filter(
            files=self._get_file_query(),
            filter_functions=[FileFilter.FILTER_BY_ID],
            file_id=file_id,
        ).first()

    def get_files(
        self, bundle: str = None, tags: List[str] = None, version: int = None   
    ) -> Query:
        """Fetches files from the store based on the specified filters.
        Args:
            bundle (str, optional): Name of the bundle to fetch files from.
            tags (List[str], optional): List of tags to filter files by.
            version (int, optional): ID of the version to fetch files from.

        Returns:
            Query: A query that match the specified filters.
        """
        query = self._get_file_query()
        if bundle:
            LOG.info(f"Fetching files from bundle {bundle}")
            query = apply_bundle_filter(
                bundles=query.join(self.File.version, self.Version.bundle),
                filter_functions=[BundleFilters.FILTER_BY_NAME],
                bundle_name=bundle
            )

        if tags:
            formatted_tags = ",".join(tags)
            LOG.info(f"Fetching files with tags in [{formatted_tags}]")

            query = apply_file_tag_filter(
                files_tags=query.join(File.tags),
                filter_functions=[FileTagFilter.FILTER_FILES_BY_TAGS],
                tags=tags,
            )

        if version:
            LOG.info(f"Fetching files from version {version}")
            query = apply_version_filter(
                versions=query.join(self.File.version),
                filter_functions=[VersionFilters.FILTER_BY_ID],
                version_id=version,
            )

        return query

    def get_files_before(
        self, bundle: str = None, tags: List[str] = None, before_date: dt.datetime = None
    ) -> List[File]:
        """Fetch files before date from store"""
        query = self.get_files(tags=tags, bundle=bundle)
        if before_date:
            query = apply_version_filter(
                versions=self._get_join_version_query(query),
                filter_functions=[VersionFilters.FILTER_BY_DATE],
                before_date=before_date,
            )
        return query.all()

    @staticmethod
    def get_files_not_on_disk(files: List[File]) -> Set[File]:
        """Return set of files that are not on disk."""
        if not files:
            return

        files_not_on_disk = [f for f in files if not Path(f.full_path).is_file()]
        return files_not_on_disk
