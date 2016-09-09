# -*- coding: utf-8 -*-
import hashlib
import logging

from path import path

from housekeeper.store import Metadata, AnalysisRun, api
from housekeeper.exc import AnalysisConflictError

BLOCKSIZE = 65536
log = logging.getLogger(__name__)


def check_existing(name, analysis_obj, run_obj):
    """Check if the analysis is already added."""
    old_analysis = api.analysis(name)
    if old_analysis:
        query = api.runs(name).filter(AnalysisRun.analyzed_at == run_obj.analyzed_at)
        old_run = query.first()
        if old_run:
            return old_analysis, old_run
        else:
            # loaded before, this is a new run
            return old_analysis, None
    else:
        # not loaded before
        return None, None


def analysis(manager, case, analysis, run):
    """Store an analysis with files to the backend."""
    log.debug("check if case is already added: %s", case.name)
    old_case = api.case(case.name)
    if old_case:
        new_case = old_case
    else:
        new_case = case

    new_case.analysis = analysis
    new_case.runs.append(run)

    meta = Metadata.query.first()
    analysis_root = meta.root_path.joinpath(new_case.name)
    if analysis_root.isdir():
        raise AnalysisConflictError("'{}' analysis output exists"
                                    .format(analysis_root))
    analysis_root.makedirs_p()

    for asset in new_case.analysis.assets:
        original_path = path(asset.original_path)
        filename = original_path.basename()
        log.info("adding asset: %s", filename)
        new_path = analysis_root.joinpath(filename)
        asset.path = new_path
        # sha1 = checksum(asset.original_path)
        # asset.checksum = sha1

    log.debug("commit new analysis to database")
    manager.add_commit(new_case)

    try:
        for asset in new_case.analysis.assets:
            log.debug("link asset: %s -> %s", asset.original_path, asset.path)
            path(asset.original_path).link(asset.path)
    except Exception as error:
        log.warn("linking error: %s -> %s", asset.original_path, asset.path)
        log.debug('cleaning up database')
        new_case.analysis.delete()
        manager.commit()
        raise error


def checksum(path):
    """Calculcate checksum for a file."""
    hasher = hashlib.sha1()
    with open(path, 'rb') as stream:
        buf = stream.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = stream.read(BLOCKSIZE)
    return hasher.hexdigest()
