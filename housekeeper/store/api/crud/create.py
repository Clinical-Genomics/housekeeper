"""This module handles adding things to the store"""

import datetime as dt
import logging
from typing import Dict, List, Tuple

from housekeeper.store import models
from housekeeper.store.api.base import BaseHandler
from housekeeper.store.api.crud.read import ReadHandler

LOG = logging.getLogger(__name__)


class CreateHandler(BaseHandler):
    """Handles adding things to the store"""

    def __init__(self):
        super().__init__()
        CreateHandler.version = ReadHandler.version
        CreateHandler.get_bundle_by_name = ReadHandler.get_bundle_by_name
        CreateHandler.get_tag = ReadHandler.get_tag

    def create_bundle(self, name: str, created_at: dt.datetime = None) -> models.Bundle:
        """Create a new file bundle."""
        new_bundle = self.Bundle(name=name, created_at=created_at)
        LOG.info("Created new bundle: %s", new_bundle.name)
        return new_bundle

    def create_bundle_and_version(
        self, data: dict
    ) -> Tuple[models.Bundle, models.Version]:
        """Build a new bundle version of files.

        The format of the input dict is defined in the `schema` module.
        """
        bundle_obj = self.get_bundle_by_name(bundle_name=data["name"])
        # These lines can be removed when decoupled from CG
        created_at = data.get("created_at", data.get("created"))
        expires_at = data.get("expires_at", data.get("expires"))
        if bundle_obj and self.get_version_by_date_and_bundle_name(
            version_date=created_at, bundle_name=bundle_obj.name
        ):
            LOG.debug("version of bundle already added")
            return None

        if bundle_obj is None:
            bundle_obj = self.create_bundle(name=data["name"], created_at=created_at)

        version_obj = self.create_version(created_at=created_at, expires_at=expires_at)
        self.update_version_with_files_and_tags(data["files"], version_obj)

        version_obj.bundle = bundle_obj
        return bundle_obj, version_obj

    def create_version(
        self, created_at: dt.datetime, expires_at: dt.datetime = None
    ) -> models.Version:
        """Create a new bundle version."""
        LOG.info("Created new version")
        new_version = self.Version(created_at=created_at, expires_at=expires_at)
        return new_version

    def create_tags_list(self, tag_names: List[str]) -> Dict[str, models.Tag]:
        """Build a list of tag objects.

        Take a list of tags, if a tag does not exist create a new tag object.
        Map the tag name to a tag object and return a list of those
        """
        tags = {}
        for tag_name in tag_names:
            tag_obj = self.get_tag(tag_name)
            if tag_obj is None:
                LOG.debug("create new tag: %s", tag_name)
                tag_obj = self.create_tag(tag_name)
            tags[tag_name] = tag_obj
        return tags

    def create_file(
        self,
        path: str,
        checksum: str = None,
        to_archive: bool = False,
        tags: List[models.Tag] = None,
    ) -> models.File:
        """Create a new file object based on the information given."""
        new_file = self.File(
            path=path, checksum=checksum, to_archive=to_archive, tags=tags
        )
        return new_file

    def create_tag(self, name: str, category: str = None) -> models.Tag:
        """Create a new tag object based on the information given."""
        new_tag = self.Tag(name=name, category=category)
        return new_tag
