import logging
from housekeeper.store.api.base import BaseHandler
from housekeeper.store.models import Bundle, File, Version, Tag
from typing import Dict, List, Tuple
from pathlib import Path

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler):
    """This class handles updating model entries in the store"""

    def update_bundle_with_version(
        self,
        data: dict,
        bundle: Bundle,
    ) -> Version:
        """Build a new version object and add it to an existing bundle"""
        created_at = data.get("created_at", data.get("created"))
        if self.get_version_by_date_and_bundle_name(
            version_date=created_at, bundle_name=bundle.name
        ):
            LOG.info("version of bundle already added")
            return None

        version_obj = self.create_version(
            created_at=created_at,
            expires_at=data.get("expires_at", data.get("expires")),
        )
        if data.get("files"):
            self.update_version_with_files_and_tags(data["files"], version_obj)

        version_obj.bundle = bundle
        return version_obj

    def update_latest_bundle_with_files(
        self,
        file_path: Path,
        bundle: Bundle,
        to_archive: bool = False,
        tags: List[str] = None,
    ) -> File:
        """Build a new file object and add it to the latest version of an existing bundle"""
        version_obj = bundle.versions[0]
        tags = tags or []
        tag_objs = [
            tag_obj for tag_name, tag_obj in self.create_tags_list(tags).items()
        ]
        new_file = self.create_file(
            path=str(file_path.absolute()),
            to_archive=to_archive,
            tags=tag_objs,
        )
        new_file.version = version_obj
        return new_file

    def update_version_with_files_and_tags(
        self, files: List[dict], version_obj: Version
    ) -> None:
        """Create file objects and the tags and add them to a version object"""

        tag_names = set(
            tag_name for file_data in files for tag_name in file_data["tags"]
        )
        tag_map = self.create_tags_list(tag_names)

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
                new_file = self.create_file(
                    path, to_archive=file_data["archive"], tags=tags
                )
                version_obj.files.append(new_file)
