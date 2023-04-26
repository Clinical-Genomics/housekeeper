"""
This module handles finding things in the store/database
"""
import datetime as dt
import logging
from pathlib import Path
from typing import List
from sqlalchemy.orm import Query, Session

from housekeeper.store.filters.bundle_filters import BundleFilters, apply_bundle_filter
from housekeeper.store.filters.file_filters import FileFilter, apply_file_filter
from housekeeper.store.filters.file_tags_filters import (
    FileTagFilter,
    apply_file_tag_filter,
)
from housekeeper.store.filters.version_bundle_filters import (
    VersionBundleFilters,
    apply_version_bundle_filter,
)
from housekeeper.store.filters.version_filters import (
    VersionFilter,
    apply_version_filter,
)
from housekeeper.store.models import Bundle, File, Tag, Version
from housekeeper.store.filters.tag_filters import TagFilter, apply_tag_filter

from .base import BaseHandler

LOG = logging.getLogger(__name__)


class FindHandler(BaseHandler):
    """Handler for searching the database"""

    def __init__(self, session: Session):
        super().__init__(session=session)

    def bundles(self):
        """Fetch bundles."""
        LOG.info("Fetching all bundles")
        return self._get_query(table=Bundle)

    def get_bundle_by_id(self, bundle_id: int) -> Bundle:
        """Fetch a bundle by id from the store."""
        LOG.info(f"Fetching bundle with id: {bundle_id}")
        return apply_bundle_filter(
            bundles=self._get_query(table=Bundle),
            filter_functions=[BundleFilters.FILTER_BY_ID],
            bundle_id=bundle_id,
        ).first()

    def get_bundle_by_name(self, bundle_name: str) -> Bundle:
        """Get a bundle by name from the store."""
        LOG.info(f"Fetching bundle with name: {bundle_name}")
        return apply_bundle_filter(
            bundles=self._get_query(table=Bundle),
            filter_functions=[BundleFilters.FILTER_BY_NAME],
            bundle_name=bundle_name,
        ).first()

    def get_version_by_date_and_bundle_name(
        self, version_date: dt.datetime, bundle_name: str
    ) -> Version:
        return apply_version_bundle_filter(
            version_bundles=self._get_join_version_bundle_query(),
            filter_functions=[VersionBundleFilters.FILTER_BY_DATE_AND_NAME],
            version_date=version_date,
            bundle_name=bundle_name,
        ).first()

    def get_version_by_id(self, version_id: int) -> Version:
        """Fetch a version from the store."""
        LOG.info(f"Fetching version with id: {version_id}")
        return apply_version_filter(
            versions=self._get_query(table=Version),
            filter_functions=[VersionFilter.FILTER_BY_ID],
            version_id=version_id,
        ).first()

    def get_tag(self, tag_name: str = None) -> Tag:
        """Return a tag from the database."""
        LOG.info(f"Fetching tag with name: {tag_name}")
        return apply_tag_filter(
            tags=self._get_query(table=Tag),
            filter_functions=[TagFilter.FILTER_BY_NAME],
            tag_name=tag_name,
        ).first()

    def get_tags(self) -> Query:
        """Return all tags from the database."""
        LOG.info("Fetching all tags")
        return self._get_query(table=Tag)

    def get_file_by_id(self, file_id: int):
        """Get a file by record id."""
        return apply_file_filter(
            files=self._get_query(table=File),
            filter_functions=[FileFilter.FILTER_BY_ID],
            file_id=file_id,
        ).first()

    def get_files(
        self,
        bundle_name: str = None,
        tag_names: List[str] = None,
        version_id: int = None,
        file_path: str = None,
    ) -> Query:
        """Fetches files from the store based on the specified filters.
        Args:
            bundle_name (str, optional): Name of the bundle to fetch files from.
            tag_names (List[str], optional): List of tags to filter files by.
            version_id (int, optional): ID of the version to fetch files from.
            path (str, optional): Path to the file to fetch.

        Returns:
            Query: A query that match the specified filters.
        """
        query = self._get_query(table=File)
        if bundle_name:
            LOG.info(f"Fetching files from bundle {bundle_name}")
            query = apply_bundle_filter(
                bundles=query.join(self.File.version, self.Version.bundle),
                filter_functions=[BundleFilters.FILTER_BY_NAME],
                bundle_name=bundle_name,
            )

        if tag_names:
            formatted_tags = ",".join(tag_names)
            LOG.info(f"Fetching files with tags in [{formatted_tags}]")

            query = apply_file_tag_filter(
                files_tags=query.join(File.tags),
                filter_functions=[FileTagFilter.FILTER_FILES_BY_TAGS],
                tag_names=tag_names,
            )

        if version_id:
            LOG.info(f"Fetching files from version {version_id}")
            query = apply_version_filter(
                versions=query.join(self.File.version),
                filter_functions=[VersionFilter.FILTER_BY_ID],
                version_id=version_id,
            )

        if file_path:
            LOG.info(f"Fetching file with path {file_path}")
            query = apply_file_filter(
                files=query,
                filter_functions=[FileFilter.FILTER_BY_PATH],
                file_path=file_path,
            )

        return query

    def get_files_before(
        self,
        bundle_name: str = None,
        tag_names: List[str] = None,
        before_date: dt.datetime = None,
    ) -> List[File]:
        """Return files before a specific date from store."""
        query = self.get_files(tag_names=tag_names, bundle_name=bundle_name)
        if before_date:
            query = apply_version_filter(
                versions=self._get_join_version_query(query),
                filter_functions=[VersionFilter.FILTER_BY_DATE],
                before_date=before_date,
            )
        return query.all()

    @staticmethod
    def get_files_not_on_disk(files: List[File]) -> List[File]:
        """Return list of files that are not on disk."""
        if not files:
            return []

        files_not_on_disk = [f for f in files if not Path(f.full_path).is_file()]
        return files_not_on_disk
