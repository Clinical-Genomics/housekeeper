"""
This module handles updating entries in the store/database.
"""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from housekeeper.store.base import BaseHandler
from housekeeper.store.filters.archive_filters import (
    ArchiveFilter,
    apply_archive_filter,
)
from housekeeper.store.models import Archive

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler):
    """Handler for updating entries in the database."""

    def __init__(self, session: Session):
        super().__init__(session=session)

    @staticmethod
    def update_archiving_time_stamp(archive: Archive) -> None:
        """Sets the archived_at timestamp of the given archive to now if no previous timestamp is
        present."""
        if archive.archived_at:
            return
        archive.archived_at = datetime.now()

    @staticmethod
    def update_retrieval_time_stamp(archive: Archive) -> None:
        """Sets the retrieved_at timestamp of the given archive to now if no previous timestamp is
        present."""
        if archive.retrieved_at:
            return
        archive.retrieved_at = datetime.now()

    def update_finished_archival_task(self, archiving_task_id: int) -> None:
        """Sets the archived_at field to now for all archives with the given archiving task id."""
        completed_archives: list[Archive] = apply_archive_filter(
            archives=self._get_query(table=Archive),
            filter_functions=[ArchiveFilter.BY_ARCHIVING_TASK_ID],
            task_id=archiving_task_id,
        ).all()
        for archive in completed_archives:
            self.update_archiving_time_stamp(archive=archive)

    def update_finished_retrieval_task(self, retrieval_task_id: int) -> None:
        """Sets the archived_at field to now for all archives with the given archiving task id."""
        completed_archives: list[Archive] = apply_archive_filter(
            archives=self._get_query(table=Archive),
            filter_functions=[ArchiveFilter.BY_RETRIEVAL_TASK_ID],
            task_id=retrieval_task_id,
        ).all()
        for archive in completed_archives:
            self.update_retrieval_time_stamp(archive=archive)

    @staticmethod
    def update_retrieval_task_id(archive: Archive, retrieval_task_id: int):
        """Sets the retrieval_task_id in the Archive entry for the provided file."""
        archive.retrieval_task_id: int = retrieval_task_id

    @staticmethod
    def update_archiving_task_id(archive: Archive, archiving_task_id: int):
        """Sets the archiving_task_id in the Archive entry for the provided file."""
        archive.archiving_task_id: int = archiving_task_id
