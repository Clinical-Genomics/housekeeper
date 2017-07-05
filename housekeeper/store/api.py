# -*- coding: utf-8 -*-
import datetime
import logging
from typing import List

import alchy

from housekeeper.add.core import AddHandler
from . import models

log = logging.getLogger(__name__)


class BaseHandler:

    Bundle = models.Bundle
    Version = models.Version
    File = models.File
    Tag = models.Tag

    def bundles(self):
        """Fetch bundles."""
        return self.Bundle.query

    def bundle(self, name: str) -> models.Bundle:
        """Fetch a bundle form the database."""
        return self.Bundle.query.filter_by(name=name).first()

    def tag(self, name: str) -> models.Tag:
        """Fetch a tag from the database."""
        return self.Tag.query.filter_by(name=name).first()

    def new_bundle(self, name: str, created_at: datetime.datetime=None) -> models.Bundle:
        """Create a new file bundle."""
        new_bundle = self.Bundle(name=name, created_at=created_at)
        return new_bundle

    def new_version(self, created_at: datetime.datetime,
                    expires_at: datetime.datetime=None) -> models.Version:
        """Create a new bundle version."""
        new_version = self.Version(created_at=created_at, expires_at=expires_at)
        return new_version

    def new_file(self, path: str, checksum: str=None, to_archive: bool=False,
                 tags: List[models.Tag]=None) -> models.File:
        """Create a new file."""
        new_file = self.File(path=path, checksum=checksum, to_archive=to_archive, tags=tags)
        return new_file

    def new_tag(self, name: str, category: str=None) -> models.Tag:
        """Create a new tag."""
        new_tag = self.Tag(name=name, category=category)
        return new_tag

    def files(self, *, bundle: str=None, tags: List[str]=None, version: int=None):
        """Fetch files from the store."""
        query = self.File.query
        if bundle:
            query = (query.join(self.File.version, self.Version.bundle)
                          .filter(self.Bundle.name == bundle))

        if tags:
            query = query.join(self.File.tags).filter(self.Tag.name.in_(tags))

        if version:
            query.join(self.File.version).filter(self.Version.id == version)

        return query


class Store(alchy.Manager, BaseHandler, AddHandler):

    """
    Handles interactions with the database in the context when a temporary
    database connection is needed, e.g. a command line interface.

    Args:
        uri (str): SQLAlchemy database connection str
    """

    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=models.Model)
