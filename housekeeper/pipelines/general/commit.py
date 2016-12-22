# -*- coding: utf-8 -*-
import logging

from path import path

from housekeeper.store import AnalysisRun, api, ExtraRunData
from housekeeper.store.utils import get_rundir
from housekeeper.exc import AnalysisConflictError

log = logging.getLogger(__name__)


def check_existing(name, run_obj):
    """Check if the analysis is already added."""
    same_date = AnalysisRun.analyzed_at == run_obj.analyzed_at
    old_run = api.runs(name).filter(same_date).first()
    return old_run


def analysis(manager, root_path, case_obj, new_run):
    """Store an analysis run with files to the backend."""
    run_root = get_rundir(root_path, case_obj.name, new_run)
    if run_root.isdir():
        raise AnalysisConflictError("'{}' analysis run output exists"
                                    .format(run_root))

    for asset in new_run.assets:
        filename = asset.basename()
        log.info("adding asset: %s", filename)
        new_path = run_root.joinpath(filename)
        asset.path = new_path

    log.debug("commit new analysis to database")
    new_run.extra = ExtraRunData()
    case_obj.runs.append(new_run)
    manager.add_commit(case_obj)

    # perform linking to the new structure
    run_root.makedirs_p()
    try:
        for asset in new_run.assets:
            log.debug("link asset: %s -> %s", asset.original_path, asset.path)
            path(asset.original_path).link(asset.path)
    except Exception as error:
        log.warn("linking error: %s -> %s", asset.original_path, asset.path)
        log.debug('cleaning up database')
        api.delete(root_path, new_run)
        manager.commit()
        raise error
