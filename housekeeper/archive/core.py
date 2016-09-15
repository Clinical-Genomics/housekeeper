# -*- coding: utf-8 -*-
import hashlib
from collections import namedtuple

from path import path

from housekeeper.store.utils import get_rundir
from .tar import tar_files

BLOCKSIZE = 65536
ArchiveGroup = namedtuple('ArchiveGroup', ['id', 'out', 'checksum'])


def compress_run(run_obj):
    """Archive a run into data+results archives."""
    case_dir = path(get_rundir(run_obj.case.name))
    run_dir = path(get_rundir(run_obj.case.name, run=run_obj))
    for group, paths in group_assets(run_obj.assets):
        run_date = run_obj.analyzed_at.date()
        group_out = case_dir.joinpath("{}.{}.tar.gz".format(run_date, group))
        filenames = [path(full_path).basename() for full_path in paths]
        tar_files(group_out, run_dir, filenames)
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
