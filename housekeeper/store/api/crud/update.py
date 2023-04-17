import logging
from housekeeper.store.api.base import BaseHandler
from housekeeper.store.models import Bundle, File, Version, Tag
from typing import Dict, List, Set
from pathlib import Path

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler):
    """This class handles updating entries in the store"""

    def update_bundle_with_version(
        self,
        data: dict,
        bundle: Bundle,
    ) -> Version:
        """Create a new version object and add it to an existing bundle."""
        created_at: dt.datetime = data.get("created_at", data.get("created"))
        if self.get_version_by_date_and_bundle_name(
            version_date=created_at, bundle_name=bundle.name
        ):
            LOG.info("Version of bundle already added")
            return None

        version: Version = self.create_version(
            created_at=created_at,
            expires_at=data.get("expires_at", data.get("expires")),
        )
        if data.get("files"):
            self.update_version_with_files_and_tags(
                files=data["files"], version_obj=version
            )

        version.bundle = bundle
        return version

    def update_latest_bundle_with_files(
        self,
        file_path: Path,
        bundle: Bundle,
        to_archive: bool = False,
        tags: List[str] = None,
    ) -> File:
        """Create a new file object and add it to the latest version of an existing bundle."""
        version: Version = bundle.versions[0]
        tags: List[Tag] = tags or []
        tags: List[Tag] = [tag for tag_name, tag in self.create_tags_dict(tags).items()]
        file: File = self.create_file(
            path=str(file_path.absolute()),
            to_archive=to_archive,
            tags=tags,
        )
        file.version = version
        return file

    def update_version_with_files_and_tags(
        self, files: List[dict], version_obj: Version
    ) -> None:
        """Create file objects and the tags and add them to a version object."""

        tag_names: Set[str] = set(
            tag_name for file in files for tag_name in file["tags"]
        )
        tag_map: Dict[str, Tag] = self.create_tags_dict(tag_names)

        for file in files:
            # This if can be removed after decoupling
            if isinstance(file["path"], str):
                paths: List[Path] = [file["path"]]
            else:
                paths: Path = file["path"]
            for path in paths:
                LOG.debug(f"adding file: {path}")
                if not Path(path).exists():
                    raise FileNotFoundError(path)
                tags: List[str] = [tag_map[tag_name] for tag_name in file["tags"]]
                file: File = self.create_file(
                    path=path, to_archive=file["archive"], tags=tags
                )
                version_obj.files.append(file)
