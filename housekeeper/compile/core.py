# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime
import hashlib
import logging

from path import path

from housekeeper.store import api
from housekeeper.store.utils import get_rundir
from .tar import tar_files

BLOCKSIZE = 65536
ArchiveGroup = namedtuple('ArchiveGroup', ['id', 'out', 'checksum'])
log = logging.getLogger(__name__)


def compile_run(run_obj):
    """High level compile function for a run."""
    groups = compress_run(run_obj)
    for group in groups:
        log.info("compressed %s archive: %s", group.id, group.out)
        category = "archive-{}".format(group.id)
        new_asset = api.add_asset(run_obj, group.out, category)
        new_asset.path = group.out
        new_asset.checksum = group.checksum
        run_obj.assets.append(new_asset)
    run_obj.compiled_at = datetime.now()


def compress_run(run_obj):
    """Archive a run into data+results archives."""
    run_dir = path(get_rundir(run_obj.case.name, run=run_obj))
    for group, paths in group_assets(run_obj.assets):
        run_date = run_obj.analyzed_at.date()
        group_out = run_dir.joinpath("{}.{}.tar.gz".format(run_date, group))
        filenames = [path(full_path).basename() for full_path in paths]
        tar_files(group_out, root_dir=run_dir, filenames=filenames)
        sha1 = checksum(group_out)
        yield ArchiveGroup(id=group, out=group_out, checksum=sha1)


def group_assets(assets):
    """Groups asset paths based on archive type."""
    # group files base on type
    groups = ('data', 'result')
    for group in groups:
        paths = [asset.path for asset in assets
                 if asset.archive_type in (group, 'meta')]
        yield group, paths


def checksum(path):
    """Calculcate checksum for a file."""
    hasher = hashlib.sha1()
    with open(path, 'rb') as stream:
        buf = stream.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = stream.read(BLOCKSIZE)
    return hasher.hexdigest()
