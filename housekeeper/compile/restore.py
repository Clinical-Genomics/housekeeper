# -*- coding: utf-8 -*-
"""Restore archived files."""
import tarfile

from path import path
import yaml

from housekeeper.store import api
from housekeeper.store.utils import get_rundir
from .tar import untar_files
from .core import checksum


def restore_run(root_path, run_obj, tar_path, archive_type):
    """Restore files from a tar archive."""
    # confirm the checksum
    sha1 = getattr(run_obj, "{}_checksum".format(archive_type))
    assert checksum(tar_path) == sha1

    # unpack the files
    run_dir = get_rundir(root_path, run_obj.case.name, run_obj)
    untar_files(run_dir, tar_path)

    # update the "local" status of all files blindly
    for asset in run_obj.assets:
        if path(asset.path).exists():
            asset.is_local = True


def run_fromtar(tar_path):
    """Get the run record for a tar archive."""
    with tarfile.open(tar_path, 'r:*') as in_handle:
        filename = 'meta.yaml'
        meta_file = in_handle.extractfile(filename)
        meta_data = yaml.load(meta_file)

    run_date = meta_data['analyzed_at'].date()
    query = api.runs(meta_data['name'], run_date=run_date)
    run_obj = query.first()
    return run_obj
