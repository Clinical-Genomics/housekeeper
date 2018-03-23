# -*- coding: utf-8 -*-
import hashlib
import logging
import os
from pathlib import Path

from housekeeper.exc import VersionIncludedError
from housekeeper.store import models

BLOCKSIZE = 65536
log = logging.getLogger(__name__)


def include_version(global_root: str, version_obj: models.Version):
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
        new_path = version_root_dir / Path(file_obj.path).name
        os.link(file_obj.path, new_path)
        log.info(f"linked file: {file_obj.path} -> {new_path}")
        file_obj.path = str(new_path).replace(f"{global_root_dir}/", '', 1)


def checksum(path):
    """Calculcate checksum for a file."""
    hasher = hashlib.sha1()
    with open(path, 'rb') as stream:
        buf = stream.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = stream.read(BLOCKSIZE)
    return hasher.hexdigest()
