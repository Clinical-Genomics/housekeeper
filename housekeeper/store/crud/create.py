"""This module handles adding things to the store"""

import datetime as dt
import logging
from pathlib import Path
from typing import Dict, Tuple

from sqlalchemy.orm import Session

from housekeeper.store.base import BaseHandler
from housekeeper.store.crud.read import ReadHandler
from housekeeper.store.models import Archive, Bundle, File, Tag, Version

LOG = logging.getLogger(__name__)


class CreateHandler(BaseHandler):
    """Handles adding things to the store"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        CreateHandler.get_bundle_by_name = ReadHandler.get_bundle_by_name
        CreateHandler.get_tag = ReadHandler.get_tag
        CreateHandler.get_version_by_date_and_bundle_name = (
            ReadHandler.get_version_by_date_and_bundle_name
        )

    def new_bundle(self, name: str, created_at: dt.datetime = None) -> Bundle:
        """Create a new file bundle."""
        new_bundle = Bundle(name=name, created_at=created_at)
        LOG.debug("Created new bundle: %s", new_bundle.name)
        return new_bundle

    def add_bundle(self, data: dict) -> Tuple[Bundle, Version] | None:
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
            bundle_obj = self.new_bundle(name=data["name"], created_at=created_at)

        version_obj = self.new_version(created_at=created_at, expires_at=expires_at)
        self._add_files_to_version(data["files"], version_obj)

        version_obj.bundle = bundle_obj
        return bundle_obj, version_obj

    def _add_files_to_version(self, files: list[dict], version_obj: Version) -> None:
        """Create file objects and the tags and add them to a version object"""

        tag_names = {tag_name for file_data in files for tag_name in file_data["tags"]}
        tag_map: dict[str, Tag] = self._build_tags(list(tag_names))

        for file_data in files:
            # This if can be removed after decoupling
            if isinstance(file_data["path"], str):
                paths = [file_data["path"]]
            else:
                paths = file_data["path"]
            for path in paths:
                LOG.debug("adding file: %s", path)
                if not Path(path).exists():
                    raise FileNotFoundError(path)
                tags = [tag_map[tag_name] for tag_name in file_data["tags"]]
                new_file = self.new_file(path, to_archive=file_data["archive"], tags=tags)
                version_obj.files.append(new_file)

    def new_version(self, created_at: dt.datetime, expires_at: dt.datetime = None) -> Version:
        """Create a new bundle version."""
        LOG.debug("Created new version")
        new_version = Version(created_at=created_at, expires_at=expires_at)
        return new_version

    def add_version(
        self,
        data: dict,
        bundle: Bundle,
    ) -> Version | None:
        """Build a new version object and add it to an existing bundle"""
        created_at = data.get("created_at", data.get("created"))
        if self.get_version_by_date_and_bundle_name(
            version_date=created_at, bundle_name=bundle.name
        ):
            LOG.debug("version of bundle already added")
            return None

        version: Version = self.new_version(
            created_at=created_at,
            expires_at=data.get("expires_at", data.get("expires")),
        )
        if data.get("files"):
            self._add_files_to_version(data["files"], version)

        version.bundle = bundle
        return version

    def add_file(
        self,
        file_path: Path,
        bundle: Bundle,
        to_archive: bool = False,
        tags: list[str] = None,
    ) -> File:
        """Build a new file object and add it to the latest version of an existing bundle."""
        version = bundle.versions[0]
        tags = tags or []
        tag_objs = [tag_obj for tag_name, tag_obj in self._build_tags(tags).items()]
        file_path_to_use: str = str(file_path)
        new_file = self.new_file(
            path=file_path_to_use,
            to_archive=to_archive,
            tags=tag_objs,
        )
        new_file.version = version
        return new_file

    def _build_tags(self, tag_names: list[str]) -> Dict[str, Tag]:
        """Build a list of tag objects.

        Take a list of tags, if a tag does not exist, create a new tag object.
        Map the tag name to a tag object and return a list of those
        """
        tags = {}
        for tag_name in tag_names:
            tag_obj = self.get_tag(tag_name)
            if tag_obj is None:
                LOG.debug("create new tag: %s", tag_name)
                tag_obj = self.new_tag(tag_name)
            tags[tag_name] = tag_obj
        return tags

    def new_file(
        self,
        path: str,
        checksum: str = None,
        to_archive: bool = False,
        tags: list[Tag] = None,
    ) -> File:
        """Create a new file object based on the information given."""
        return File(path=path, checksum=checksum, to_archive=to_archive, tags=tags)

    def new_tag(self, name: str, category: str = None) -> Tag:
        """Create a new tag object based on the information given."""
        new_tag = Tag(name=name, category=category)
        return new_tag

    def create_archive(self, file_id: int, archiving_task_id: int) -> Archive:
        """Creates an archive object to the given file, with the given archive task id."""
        return Archive(file_id=file_id, archiving_task_id=archiving_task_id)
