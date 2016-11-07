# -*- coding: utf-8 -*-
import logging

from path import path

from housekeeper.store import AnalysisRun, api
from housekeeper.store.utils import get_rundir
from housekeeper.exc import AnalysisConflictError

log = logging.getLogger(__name__)


def check_existing(name, run_obj):
    """Check if the analysis is already added."""
    same_date = AnalysisRun.analyzed_at == run_obj.analyzed_at
    old_run = api.runs(name).filter(same_date).first()
    return old_run


def analysis(manager, root_path, case, run):
    """Store an analysis run with files to the backend."""
    log.debug("check if case is already added: %s", case.name)
    old_case = api.case(case.name)
    if old_case:
        new_case = old_case
    else:
        new_case = case

    run_root = get_rundir(root_path, new_case.name, run)
    if run_root.isdir():
        raise AnalysisConflictError("'{}' analysis run output exists"
                                    .format(run_root))

    for sample in run.samples:
        existing_sample = api.sample(sample.lims_id)
        if existing_sample:
            log.debug("found existing sample - using that: %s", sample.lims_id)
            run.samples.remove(sample)
            run.samples.append(existing_sample)
            for asset in run.assets:
                if asset.sample and asset.sample == sample:
                    asset.sample = existing_sample
            # lift the new sample skeleton from the session
            manager.expunge(sample)

    for asset in run.assets:
        filename = asset.basename()
        log.info("adding asset: %s", filename)
        new_path = run_root.joinpath(filename)
        asset.path = new_path

    log.debug("commit new analysis to database")
    new_case.runs.append(run)
    manager.add_commit(new_case)

    # perform linking to the new structure
    run_root.makedirs_p()
    try:
        for asset in run.assets:
            log.debug("link asset: %s -> %s", asset.original_path, asset.path)
            path(asset.original_path).link(asset.path)
    except Exception as error:
        log.warn("linking error: %s -> %s", asset.original_path, asset.path)
        log.debug('cleaning up database')
        api.delete(root_path, run)
        manager.commit()
        raise error
