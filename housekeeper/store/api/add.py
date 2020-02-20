# -*- coding: utf-8 -*-
"""This module handles adding things to the store"""

import logging
from pathlib import Path
from typing import List
import datetime as dt

from housekeeper.store import models
from housekeeper.store.api.base import BaseHandler
from housekeeper.store.api.find import FindHandler


LOG = logging.getLogger(__name__)


class AddHandler(BaseHandler):
    """Handles adding things to the store"""

    def __init__(self):
        super().__init__()
        AddHandler.version = FindHandler.version
        AddHandler.bundle = FindHandler.bundle
        AddHandler.tag = FindHandler.tag

    def add_bundle(self, data: dict) -> (models.Bundle, models.Version):
        """Build a new bundle version of files.

        The format of the input dict is defined in the `schema` module.
        """
        bundle_obj = self.bundle(data["name"])
        if bundle_obj and self.version(bundle_obj.name, data["created"]):
            LOG.debug("version of bundle already added")
            return None

        if bundle_obj is None:
            bundle_obj = self.new_bundle(name=data["name"], created_at=data["created"])

        version_obj = self.new_version(
            created_at=data["created"], expires_at=data.get("expires")
        )

        tag_names = set(
            tag_name for file_data in data["files"] for tag_name in file_data["tags"]
        )
        tag_map = self._build_tags(tag_names)

        for file_data in data["files"]:
            if isinstance(file_data["path"], str):
                paths = [file_data["path"]]
            else:
                paths = file_data["path"]
            for path in paths:
                LOG.debug("adding file: %s", path)
                if not Path(path).exists():
                    raise FileNotFoundError(path)
                tags = [tag_map[tag_name] for tag_name in file_data["tags"]]
                new_file = self.new_file(
                    path, to_archive=file_data["archive"], tags=tags
                )
                version_obj.files.append(new_file)

        version_obj.bundle = bundle_obj
        return bundle_obj, version_obj

    def _build_tags(self, tag_names: List[str]) -> dict:
        """Build a list of tag objects."""
        tags = {}
        for tag_name in tag_names:
            tag_obj = self.tag(tag_name)
            if tag_obj is None:
                LOG.debug("create new tag: %s", tag_name)
                tag_obj = self.new_tag(tag_name)
            tags[tag_name] = tag_obj
        return tags

    def new_bundle(self, name: str, created_at: dt.datetime = None) -> models.Bundle:
        """Create a new file bundle."""
        new_bundle = self.Bundle(name=name, created_at=created_at)
        return new_bundle

    def new_version(
        self, created_at: dt.datetime, expires_at: dt.datetime = None
    ) -> models.Version:
        """Create a new bundle version."""
        new_version = self.Version(created_at=created_at, expires_at=expires_at)
        return new_version

    def new_file(
        self,
        path: str,
        checksum: str = None,
        to_archive: bool = False,
        tags: List[models.Tag] = None,
    ) -> models.File:
        """Create a new file."""
        new_file = self.File(
            path=path, checksum=checksum, to_archive=to_archive, tags=tags
        )
        return new_file

    def new_tag(self, name: str, category: str = None) -> models.Tag:
        """Create a new tag."""
        new_tag = self.Tag(name=name, category=category)
        return new_tag
