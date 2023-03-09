"""
This module handles finding things in the store/database
"""
import datetime as dt
import logging
from pathlib import Path
from typing import Iterable, List, Set
from sqlalchemy.orm import Query
from housekeeper.store.filters.file_tags_filters import FileTagFilters, apply_file_tag_filters

from housekeeper.store.models import Bundle, File, Tag, Version
from housekeeper.store.filters.file_filters import FileFilters, apply_file_filters
from housekeeper.store.filters.bundle_filters import apply_bundle_filter, BundleFilters
from housekeeper.store.filters.version_filters import apply_version_filter, VersionFilters
from housekeeper.store.filters.version_bundle_filters import apply_version_bundle_filter, VersionBundleFilters

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

    def _get_version_bundle_query(self) -> Query:
        """Return version bundle query."""
        return self.Version.query.join(Version.bundle)

    def _get_file_tag_query(self) -> Query:
        """Return file tag query."""
        return self.File.query.join(File.tags)

    def bundle(self, name: str = None, bundle_id: int = None) -> Bundle:
        """Fetch a bundle from the store."""
        if bundle_id:
            LOG.info(f"Fetching bundle with id: {bundle_id}")
            return apply_bundle_filter(
                bundles=self._get_bundle_query(),
                filter_functions=[BundleFilters.FILTER_BY_ID],
                bundle_id=bundle_id,
            ).first()

        LOG.info(f"Fetching bundle with name: {name}")
        return apply_bundle_filter(
            bundles=self._get_bundle_query(),
            filter_functions=[BundleFilters.FILTER_BY_NAME],
            bundle_name=name,
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
            version_bundles=self._get_version_bundle_query(),
            filter_functions=[VersionBundleFilters.FILTER_BY_DATE_AND_NAME],
            version_date=date,
            bundle_name=bundle,
        ).first()

    def tag(self, name: str) -> Tag:
        """Fetch a tag from the database."""
        return self.Tag.filter_by(name=name).first()

    def tags(self) -> List:
        """Fetch all tags from the database."""
        return self.Tag.query

    def file_(self, file_id: int):
        """Get a file by record id."""
        return apply_file_filters(
            files=self._get_file_query(),
            filter_functions=[FileFilters.FILTER_BY_ID],
            file_id=file_id,
        ).first()

    def files(
        self, bundle: str = None, tags: List[str] = None, version: int = None
    ) -> Iterable[File]:
        """Fetch files from the store."""
        query = self._get_file_query()
        if bundle:
            LOG.info(f"Fetching files from bundle {bundle}")
            query = query.join(self.File.version, self.Version.bundle).filter(
                self.Bundle.name == bundle
            )

        if tags:
            formatted_tags = ",".join(tags)
            LOG.info(f"Fetching files with tags in [{formatted_tags}]")

            query = apply_file_tag_filters(
                files_tags=query.join(File.tags),
                filter_functions=[FileTagFilters.FILTER_FILES_BY_TAGS],
                tags=tags,
            )

        if version:
            LOG.info(f"Fetching files from version {version}")
            query = query.join(self.File.version).filter(self.Version.id == version)

        return query

    def files_before(
        self, bundle: str = None, tags: List[str] = None, before_date: dt.datetime = None
    ) -> List[File]:
        """Fetch files before date from store"""
        query = self.files(tags=tags, bundle=bundle)
        if before_date:
            query = apply_version_filter(
                versions=query.join(Version),
                filter_functions=[VersionFilters.FILTER_BY_DATE],
                before_date=before_date,
            )
        return query.all()

    @staticmethod
    def files_not_on_disk(files: List[File]) -> Set[File]:
        """Return set of files that are not on disk."""
        if not files:
            return

        files_not_on_disk = [f for f in files if not Path(f.full_path).is_file()]
        return files_not_on_disk
