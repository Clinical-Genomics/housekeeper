"""This module handles reading the database."""

import datetime
import datetime as dt
import logging
from pathlib import Path

from sqlalchemy.orm import Query, Session

from housekeeper.store.base import BaseHandler
from housekeeper.store.filters.archive_filters import (
    ArchiveFilter,
    apply_archive_filter,
)
from housekeeper.store.filters.bundle_filters import BundleFilters, apply_bundle_filter
from housekeeper.store.filters.file_filters import FileFilter, apply_file_filter
from housekeeper.store.filters.tag_filters import TagFilter, apply_tag_filter
from housekeeper.store.filters.version_bundle_filters import (
    VersionBundleFilters,
    apply_version_bundle_filter,
)
from housekeeper.store.filters.version_filters import (
    VersionFilter,
    apply_version_filter,
)
from housekeeper.store.models import Archive, Bundle, File, Tag, Version

LOG = logging.getLogger(__name__)


class ReadHandler(BaseHandler):
    """Handler for searching the database"""

    def __init__(self, session: Session):
        super().__init__(session=session)

    def bundles(self):
        """Fetch bundles."""
        LOG.debug("Fetching all bundles")
        return self._get_query(table=Bundle)

    def get_bundle_by_id(self, bundle_id: int) -> Bundle:
        """Fetch a bundle by id from the store."""
        LOG.debug(f"Fetching bundle with id: {bundle_id}")
        return apply_bundle_filter(
            bundles=self._get_query(table=Bundle),
            filter_functions=[BundleFilters.BY_ID],
            bundle_id=bundle_id,
        ).first()

    def get_bundle_by_name(self, bundle_name: str) -> Bundle:
        """Get a bundle by name from the store."""
        LOG.debug(f"Fetching bundle with name: {bundle_name}")
        return apply_bundle_filter(
            bundles=self._get_query(table=Bundle),
            filter_functions=[BundleFilters.BY_NAME],
            bundle_name=bundle_name,
        ).first()

    def get_version_by_date_and_bundle_name(
        self, version_date: dt.datetime, bundle_name: str
    ) -> Version:
        return apply_version_bundle_filter(
            version_bundles=self._get_join_version_bundle_query(),
            filter_functions=[VersionBundleFilters.BY_DATE_AND_NAME],
            version_date=version_date,
            bundle_name=bundle_name,
        ).first()

    def get_version_by_id(self, version_id: int) -> Version:
        """Fetch a version from the store."""
        LOG.debug(f"Fetching version with id: {version_id}")
        return apply_version_filter(
            versions=self._get_query(table=Version),
            filter_functions=[VersionFilter.BY_ID],
            version_id=version_id,
        ).first()

    def get_tag(self, tag_name: str = None) -> Tag:
        """Return a tag from the database."""
        LOG.debug(f"Fetching tag with name: {tag_name}")
        return apply_tag_filter(
            tags=self._get_query(table=Tag),
            filter_functions=[TagFilter.BY_NAME],
            tag_name=tag_name,
        ).first()

    def get_tags(self) -> Query:
        """Return all tags from the database."""
        LOG.debug("Fetching all tags")
        return self._get_query(table=Tag)

    def get_file_by_id(self, file_id: int) -> File | None:
        """Get a file by record id."""
        return apply_file_filter(
            files=self._get_query(table=File),
            filter_functions=[FileFilter.BY_ID],
            file_id=file_id,
        ).first()

    def get_files(
        self,
        bundle_name: str = None,
        tag_names: list[str] = None,
        version_id: int = None,
        file_path: str = None,
        local_only: bool = None,
        remote_only: bool = None,
    ) -> Query:
        """Return a query with specified filters for files from the database."""
        query: Query = self._get_query(table=File)
        if bundle_name:
            LOG.debug(f"Fetching files from bundle {bundle_name}")
            query: Query = apply_bundle_filter(
                bundles=query.join(File.version).join(Version.bundle),
                filter_functions=[BundleFilters.BY_NAME],
                bundle_name=bundle_name,
            )
        if tag_names:
            formatted_tags: str = ",".join(tag_names)
            LOG.debug(f"Fetching files with tags in [{formatted_tags}]")

            query: Query = apply_file_filter(
                files=query.join(File.tags),
                filter_functions=[FileFilter.FILES_BY_TAGS],
                tag_names=tag_names,
            )
        if version_id:
            LOG.debug(f"Fetching files from version {version_id}")
            query: Query = apply_version_filter(
                versions=query.join(File.version),
                filter_functions=[VersionFilter.BY_ID],
                version_id=version_id,
            )
        if file_path:
            LOG.debug(f"Fetching file with path {file_path}")
            query: Query = apply_file_filter(
                files=query,
                filter_functions=[FileFilter.BY_PATH],
                file_path=file_path,
            )
        if local_only:
            query: Query = apply_file_filter(
                files=query,
                filter_functions=[FileFilter.IS_LOCAL],
            )
        if remote_only:
            query: Query = apply_file_filter(
                files=query,
                filter_functions=[FileFilter.IS_REMOTE],
                is_archived=False,
            )
        return query

    def get_files_before(
        self,
        bundle_name: str = None,
        tag_names: list[str] = None,
        before_date: dt.datetime = None,
    ) -> list[File]:
        """Return files before a specific date from store."""
        query = self.get_files(tag_names=tag_names, bundle_name=bundle_name)
        if before_date:
            query = apply_version_filter(
                versions=self._get_join_version_query(query),
                filter_functions=[VersionFilter.BY_DATE],
                before_date=before_date,
            )
        return query.all()

    @staticmethod
    def get_files_not_on_disk(files: list[File]) -> list[File]:
        """Return list of files that are not on disk."""
        if not files:
            return []

        files_not_on_disk = [f for f in files if not Path(f.full_path).is_file()]
        return files_not_on_disk

    def get_archived_files_for_bundle(self, bundle_name: str, tags: list | None) -> list[File]:
        """Returns all files in the given bundle, with the given tags, and are archived."""
        files_filtered_on_bundle: Query = apply_bundle_filter(
            bundles=self._get_join_file_tags_archive_query(),
            bundle_name=bundle_name,
            filter_functions=[BundleFilters.BY_NAME],
        )
        return apply_file_filter(
            files=files_filtered_on_bundle,
            filter_functions=[
                FileFilter.FILES_BY_TAGS,
                FileFilter.FILES_BY_IS_ARCHIVED,
            ],
            is_archived=True,
            tag_names=tags,
        ).all()

    def get_non_archived_files_for_bundle(self, bundle_name: str, tags: list | None) -> list[File]:
        """Returns all files in the given bundle, with the given tags, and are not archived."""
        files_filtered_on_bundle: Query = apply_bundle_filter(
            bundles=self._get_join_file_tags_archive_query(),
            bundle_name=bundle_name,
            filter_functions=[BundleFilters.BY_NAME],
        )
        return apply_file_filter(
            files=files_filtered_on_bundle,
            filter_functions=[
                FileFilter.FILES_BY_TAGS,
                FileFilter.FILES_BY_IS_ARCHIVED,
            ],
            is_archived=False,
            tag_names=tags,
        ).all()

    def get_ongoing_archivals(self) -> list[Archive]:
        """Returns all archiving tasks in the archive table, for entries where the archiving
        field is empty."""
        return apply_archive_filter(
            archives=self._get_query(table=Archive),
            filter_functions=[ArchiveFilter.ARCHIVING_ONGOING],
        ).all()

    def get_ongoing_retrievals(self) -> list[Archive]:
        """Returns all retrieval tasks in the archive table, for entries where the retrieved_at
        field is empty."""
        return apply_archive_filter(
            archives=self._get_query(table=Archive),
            filter_functions=[ArchiveFilter.RETRIEVAL_ONGOING],
        ).all()

    def get_bundle_name_from_file_path(self, file_path: str) -> str:
        """Return the bundle name for the specified file."""
        return self.get_files(file_path=file_path).first().version.bundle.name

    def get_non_archived_files(self, tag_names: list[str], limit: int | None = None) -> list[File]:
        """Return all spring files which are not marked as archived in Housekeeper."""
        return (
            apply_file_filter(
                self._get_join_file_tags_archive_query(),
                filter_functions=[
                    FileFilter.FILES_BY_TAGS,
                    FileFilter.FILES_BY_IS_ARCHIVED,
                ],
                tag_names=tag_names,
                is_archived=False,
            )
            .limit(limit)
            .all()
        )

    def get_archives(
        self, archival_task_id: int = None, retrieval_task_id: int = None
    ) -> list[Archive] | None:
        """Returns all entries in the archive table with the specified archival/retrieval task id."""
        if not archival_task_id and not retrieval_task_id:
            return self._get_query(table=Archive).all()
        if archival_task_id and retrieval_task_id:
            return apply_archive_filter(
                archives=apply_archive_filter(
                    archives=self._get_query(table=Archive),
                    filter_functions=[ArchiveFilter.BY_ARCHIVING_TASK_ID],
                    task_id=archival_task_id,
                ),
                filter_functions=[ArchiveFilter.BY_RETRIEVAL_TASK_ID],
                task_id=retrieval_task_id,
            ).all()
        if archival_task_id:
            return apply_archive_filter(
                archives=self._get_query(table=Archive),
                filter_functions=[ArchiveFilter.BY_ARCHIVING_TASK_ID],
                task_id=archival_task_id,
            ).all()

        return apply_archive_filter(
            archives=self._get_query(table=Archive),
            filter_functions=[ArchiveFilter.BY_RETRIEVAL_TASK_ID],
            task_id=retrieval_task_id,
        ).all()

    def get_files_retrieved_before(
        self, date: datetime, tag_names: list[str] | None = None
    ) -> list[File]:
        """Returns all files which were retrieved before the given date."""
        old_enough_files: Query = apply_archive_filter(
            archives=self._get_join_file_tags_archive_query(),
            filter_functions=[ArchiveFilter.BY_RETRIEVED_BEFORE],
            retrieved_before=date,
        )
        if tag_names:
            return apply_file_filter(
                files=old_enough_files,
                filter_functions=[FileFilter.FILES_BY_TAGS],
                tag_names=tag_names,
            ).all()
        return old_enough_files.all()
