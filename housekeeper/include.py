"""Module for code to include files in housekeeper"""

import hashlib
import logging
import os
from pathlib import Path

from housekeeper.exc import VersionIncludedError
from housekeeper.store.models import Version

BLOCKSIZE = 65536
EMPTY_STR = ""
LOG = logging.getLogger(__name__)


def link_file(file_path: Path, new_path: Path, hardlink: bool = True) -> None:
    """Create a link for a file"""
    if hardlink:
        LOG.debug("Creating hardlink")
        os.link(file_path.resolve(), new_path)
    else:
        LOG.debug("Creating softlink")
        new_path.symlink_to(file_path)
    LOG.info("linked file: %s -> %s", file_path, new_path)


def include_version(global_root: str, version_obj: Version, hardlink: bool = True):
    """Include files in existing bundle version.

    Including a file means to link them into a folder in the root directory
    """
    LOG.info("Use global root path %s", global_root)
    global_root_dir = Path(global_root)
    if version_obj.included_at:
        raise VersionIncludedError(f"version included on {version_obj.included_at}")

    # generate root directory
    version_root_dir = global_root_dir / version_obj.relative_root_dir
    version_root_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("created new bundle version dir: %s", version_root_dir)

    for file_obj in version_obj.files:
        # hardlink file to the internal structure
        file_obj_path = Path(file_obj.path)
        new_path = version_root_dir / file_obj_path.name
        link_file(file_path=file_obj_path, new_path=new_path, hardlink=hardlink)
        file_obj.path = str(new_path).replace(f"{global_root_dir}/", EMPTY_STR, 1)


def checksum(path: Path) -> str:
    """Calculcate checksum for a file."""
    hasher = hashlib.sha1()
    with open(path, "rb") as stream:
        buf = stream.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = stream.read(BLOCKSIZE)
    return hasher.hexdigest()


def same_file_exists_in_bundle_directory(
    file_path: Path, bundle_root_path=Path, version=Version
) -> bool:
    housekeeper_file_path: Path = Path(bundle_root_path, version.relative_root_dir, file_path.name)
    return housekeeper_file_path.exists() and Path.samefile(file_path, housekeeper_file_path)


def link_to_relative_path(file_path: Path, root_path: Path, version: Version) -> None:
    """Link the given absolute path to the path of the given bundle version."""
    housekeeper_path: Path = Path(root_path, version.relative_root_dir, file_path.name)
    link_file(file_path=file_path, new_path=housekeeper_path, hardlink=True)


def relative_path(version: Version, file: Path) -> Path:
    return Path(version.relative_root_dir, file.name)
