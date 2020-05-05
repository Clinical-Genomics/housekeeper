"""Module for code to include files in housekeeper"""
import hashlib
import logging
import os
from pathlib import Path

from housekeeper.exc import VersionIncludedError
from housekeeper.store import models

BLOCKSIZE = 65536
EMPTY_STR = ""
log = logging.getLogger(__name__)


def include_version(
    global_root: str, version_obj: models.Version, hardlink: bool = True
):
    """Include files in existing bundle version."""
    global_root_dir = Path(global_root)
    if version_obj.included_at:
        raise VersionIncludedError(f"version included on {version_obj.included_at}")

    # generate root directory
    version_root_dir = global_root_dir / version_obj.relative_root_dir
    version_root_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"created new bundle version dir: {version_root_dir}")

    for file_obj in version_obj.files:
        # hardlink file to the internal structure
        file_obj_path = Path(file_obj.path)
        new_path = version_root_dir / file_obj_path.name
        if hardlink:
            os.link(file_obj_path.resolve(), new_path)
        else:
            os.symlink(file_obj_path.resolve(), new_path)
        log.info(f"linked file: {file_obj.path} -> {new_path}")
        file_obj.path = str(new_path).replace(f"{global_root_dir}/", EMPTY_STR, 1)


def checksum(path):
    """Calculcate checksum for a file."""
    hasher = hashlib.sha1()
    with open(path, "rb") as stream:
        buf = stream.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = stream.read(BLOCKSIZE)
    return hasher.hexdigest()
