# -*- coding: utf-8 -*-
import datetime
import logging

from path import path

from .models import AnalysisRun, Case
from .utils import get_rundir

log = logging.getLogger(__name__)


def case(name):
    """Get a case from the database.

    Args:
        name (str): the unique name of the analysis

    Returns:
        Case or None: the case or None if not found
    """
    # 'name' is a unique column so it will always return 1 or 0 records
    case_obj = Case.query.filter_by(name=name).first()
    return case_obj


def cases(query_str=None):
    """Get multiple cases from the database."""
    query = Case.query.order_by(Case.created_at.desc())
    if query_str:
        query = query.filter(Case.name.like("%{}%".format(query_str)))
    return query


def runs(case_name):
    """Get runs for a case from the database.

    Args:
        case_name (str): the unique name of the case

    Returns:
        Query: all runs for the case
    """
    run_query = (AnalysisRun.query.join(AnalysisRun.case)
                            .filter(Case.name == case_name)
                            .order_by(AnalysisRun.created_at.desc()))
    return run_query


def delete(run_obj):
    """Delete an analysis run along with related files on the system.

    Args:
        run_obj (AnalysisRun): the analysis run to delete
    """
    run_dir = get_rundir(run_obj.case.name, run_obj)
    log.info("removing files under: %s", run_dir)
    run_dir.rmtree_p()
    run_obj.delete()


def archive(run_obj):
    """Archive an analysis run.

    Args:
        run_obj (AnalysisRun): the analysis run to archive
    """
    # mark case as "archived"
    run_obj.archived_at = datetime.datetime.now()


def clean_up(run_obj, keep_archive=False):
    """Clean up files for an analysis."""
    # remove all files that aren't marked for archive
    for asset in run_obj.assets:
        if not asset.archive_type or not keep_archive:
            log.info("removing asset", asset.path)
            path(asset.path).remove()
            asset.delete()

    run_obj.cleanedup_at = datetime.datetime.now()


def postpone(run_obj, time=datetime.timedelta(days=30)):
    """Postpone the automatic archival of analysis by X time."""
    run_obj.will_cleanup_at += time
