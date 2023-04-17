import datetime as dt
import logging
from typing import Dict, List, Tuple

from housekeeper.store.models import Bundle, File, Version, Tag
from housekeeper.store.api.base import BaseHandler
from housekeeper.store.api.crud.read import ReadHandler

LOG = logging.getLogger(__name__)


class CreateHandler(BaseHandler):
    """This module handles creating entries in the store."""

    def __init__(self):
        super().__init__()
        CreateHandler.version = ReadHandler.version
        CreateHandler.get_bundle_by_name = ReadHandler.get_bundle_by_name
        CreateHandler.get_tag = ReadHandler.get_tag

    def create_bundle(self, name: str, created_at: dt.datetime = None) -> Bundle:
        """Create a new file bundle."""
        bundle: Bundle = self.Bundle(name=name, created_at=created_at)
        LOG.info(f"Created new bundle: {bundle.name}")
        return bundle

    def create_bundle_and_version(self, data: dict) -> Tuple[Bundle, Version]:
        """Create a new bundle version of files.

        The format of the input dict is defined in the `schema` module.
        """
        bundle: Bundle = self.get_bundle_by_name(bundle_name=data["name"])
        # These lines can be removed when decoupled from CG
        created_at: dt.datetime = data.get("created_at", data.get("created"))
        expires_at: dt.datetime = data.get("expires_at", data.get("expires"))
        if bundle and self.get_version_by_date_and_bundle_name(
            version_date=created_at, bundle_name=bundle.name
        ):
            LOG.debug("version of bundle already created")
            return None

        if bundle is None:
            bundle: Bundle = self.create_bundle(
                name=data["name"], created_at=created_at
            )

        version: Version = self.create_version(
            created_at=created_at, expires_at=expires_at
        )
        self.update_version_with_files_and_tags(
            files=data["files"], version_obj=version
        )

        version.bundle = bundle
        return bundle, version

    def create_version(
        self, created_at: dt.datetime, expires_at: dt.datetime = None
    ) -> Version:
        """Create a new bundle version."""
        LOG.info("Created new version")
        return self.Version(created_at=created_at, expires_at=expires_at)

    def create_tags_dict(self, tag_names: List[str]) -> Dict[str, Tag]:
        """Build a dictionary of tag objects.

        Take a list of tags, if a tag does not exist create a new tag object.
        Map the tag name to a tag object and return a list of those
        """
        tags: Dict = {}
        for tag_name in tag_names:
            tag: Tag = self.get_tag(tag_name)
            if tag is None:
                LOG.debug(f"create new tag: {tag_name}")
                tag: Tag = self.create_tag(tag_name)
            tags[tag_name] = tag
        return tags

    def create_file(
        self,
        path: str,
        checksum: str = None,
        to_archive: bool = False,
        tags: List[Tag] = None,
    ) -> File:
        """Create a new file object ."""
        return self.File(path=path, checksum=checksum, to_archive=to_archive, tags=tags)

    def create_tag(self, name: str, category: str = None) -> Tag:
        """Create a new tag object."""
        return self.Tag(name=name, category=category)
