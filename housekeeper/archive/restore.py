# -*- coding: utf-8 -*-
"""Restore archived files."""
from path import path
import yaml

from housekeeper.store.utils import get_rundir
from .tar import untar_files
from .core import checksum


def restore(run_obj, tar_path, archive_type):
    """Restore files from a tar archive."""
    # confirm the checksum
    sha1 = getattr(run_obj, "{}_checksum".format(archive_type))
    assert checksum(tar_path) == sha1

    # unpack the files
    run_dir = get_rundir(run_obj.case.name, run_obj)
    untar_files(run_dir, tar_path)

    # confirm with the data from the meta file
    meta_path = path(run_dir).joinpath('meta.yaml')
    with meta_path.open('r') as stream:
        meta_data = yaml.load(stream)
    assert meta_data['name'] == run_obj.case.name
    assert meta_data['analyzed_at'] == run_obj.analyzed_at

    # update the "local" status of all files blindly
    for asset in run_obj.assets:
        if path(asset.path).exists():
            asset.is_local = True
