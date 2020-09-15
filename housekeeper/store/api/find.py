"""
This module handles finding things in the store/database
"""
import datetime as dt
import logging
from pathlib import Path
from typing import Iterable, List

from sqlalchemy import func as sqlalchemy_func

from housekeeper.date import get_date
from housekeeper.store import models

from .base import BaseHandler

LOG = logging.getLogger(__name__)


class FindHandler(BaseHandler):
    """Handler for searching the database"""

    def bundles(self):
        """Fetch bundles."""
        LOG.info("Fetching all bundles")
        return self.Bundle.query

    def bundle(self, name: str = None, bundle_id: int = None) -> models.Bundle:
        """Fetch a bundle from the store."""
        if bundle_id:
            LOG.info("Fetching bundle with id: %s", bundle_id)
            return self.Bundle.get(bundle_id)
        LOG.info("Fetching bundle with name: %s", name)
        return self.Bundle.filter_by(name=name).first()

    def version(
        self, bundle: str = None, date: dt.datetime = None, version_id: int = None
    ) -> models.Version:
        """Fetch a version from the store."""
        if version_id:
            LOG.info("Fetching version with id: %s", version_id)
            return self.Version.get(version_id)

        return (
            self.Version.query.join(models.Version.bundle)
            .filter(models.Bundle.name == bundle, models.Version.created_at == date)
            .first()
        )

    def versions(self, bundle: str) -> List:
        """Fetch a version from the store."""
        query = self.Version.query
        if bundle:
            query = query.join(models.Version.bundle).filter(models.Bundle.name == bundle)
        return query

    def tag(self, name: str) -> models.Tag:
        """Fetch a tag from the database."""
        return self.Tag.filter_by(name=name).first()

    def tags(self) -> List:
        """Fetch all tags from the database."""
        return self.Tag.query

    def file_(self, file_id: int):
        """Get a file by record id."""
        return self.File.get(file_id)

    def files(
        self, *, bundle: str = None, tags: List[str] = None, version: int = None, path: str = None
    ) -> Iterable[models.File]:
        """Fetch files from the store."""
        query = self.File.query
        if bundle:
            LOG.info("Fetching files from bundle %s", bundle)
            query = query.join(self.File.version, self.Version.bundle).filter(
                self.Bundle.name == bundle
            )

        if tags:
            LOG.info("Fetching files with tags in [%s]", ",".join(tags))
            # require records to match ALL tags
            query = (
                query.join(self.File.tags)
                .filter(self.Tag.name.in_(tags))
                .group_by(models.File.id)
                .having(sqlalchemy_func.count(models.Tag.name) == len(tags))
            )

        if version:
            LOG.info("Fetching files from version %s", version)
            query = query.join(self.File.version).filter(self.Version.id == version)

        if path:
            LOG.info("Fetching files with path %s", path)
            query = query.filter_by(path=path)

        return query

    def files_before(
        self, *, bundle: str = None, tags: List[str] = None, before: str = None
    ) -> models.File:
        """Fetch files before date from store"""
        query = self.files(tags=tags, bundle=bundle)
        if before:
            try:
                before_dt = get_date(before)
            except ValueError:
                before_dt = get_date(before, "%Y-%m-%d %H:%M:%S")
            query = query.join(models.Version).filter(models.Version.created_at < before_dt)

        return query

    @staticmethod
    def files_ondisk(file_objs: models.File) -> set:
        """Returns a list of files that are on disk."""

        files_on_disk = {file_obj for file_obj in file_objs if Path(file_obj.full_path).is_file()}
        return files_on_disk
