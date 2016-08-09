# -*- coding: utf-8 -*-
import hashlib
import logging

from path import path

from housekeeper.store import Metadata, Analysis
from housekeeper.exc import AnalysisConflictError

BLOCKSIZE = 65536
log = logging.getLogger(__name__)


def analysis(manager, analysis_obj):
    """Store an analysis with files to the backend."""
    log.debug("check if analysis is already added: %s", analysis_obj.name)
    if Analysis.query.filter_by(name=analysis_obj.name).first():
        raise AnalysisConflictError(
            "'{}' already added".format(analysis_obj.name))

    meta = Metadata.query.first()
    analysis_root = path(meta.analyses_root).joinpath(analysis_obj.name)
    if analysis_root.isdir():
        raise AnalysisConflictError(
            "'{}' already exists".format(analysis_root))
    analysis_root.makedirs_p()

    for asset in analysis_obj.assets:
        original_path = path(asset.original_path)
        filename = original_path.basename()
        new_path = analysis_root.joinpath(filename)
        asset.path = new_path
        # sha1 = checksum(asset.original_path)
        # asset.checksum = sha1

    log.debug("commit new analysis to database")
    manager.add_commit(analysis_obj)

    try:
        for asset in analysis_obj.assets:
            log.debug("link asset: %s -> %s", asset.original_path, asset.path)
            path(asset.original_path).link(asset.path)
    except Exception:
        log.warn("linking error, cleaning up database")
        analysis_obj.delete()


def checksum(path):
    """Calculcate checksum for a file."""
    hasher = hashlib.sha1()
    with open(path, 'rb') as stream:
        buf = stream.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = stream.read(BLOCKSIZE)
    return hasher.hexdigest()
