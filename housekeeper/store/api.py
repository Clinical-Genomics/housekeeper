# -*- coding: utf-8 -*-
import datetime
import logging

from alchy import Manager
from path import path

from .models import AnalysisRun, Asset, Case, Model, Sample
from .utils import get_rundir

log = logging.getLogger(__name__)


def manager(db_uri):
    log.debug('open connection to database: %s', db_uri)
    db = Manager(config=dict(SQLALCHEMY_DATABASE_URI=db_uri), Model=Model,
                 session_options=dict(autoflush=False))
    return db


def assets(case_name=None, sample=None, category=None):
    """Get files from the database."""
    query = Asset.query
    if case_name:
        query = (query.join(Asset.run, AnalysisRun.case)
                      .filter(Case.name == case_name))
    if sample:
        query = query.join(Asset.sample).filter(Sample.name == sample)
    if category:
        query = query.filter(Asset.category == category)
    return query


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


def runs(case_name, run_date=None):
    """Get runs for a case from the database.

    Args:
        case_name (str): the unique name of the case

    Returns:
        Query: all runs for the case
    """
    if run_date:
        delta = datetime.timedelta(days=1)
        next_day = run_date + delta
        condition = AnalysisRun.analyzed_at.between(run_date, next_day)
        return AnalysisRun.query.filter(condition)
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
    delete_dir(run_dir)
    run_obj.delete()


def clean_up(run_obj, force=False):
    """Clean up files for an analysis."""
    # check if run is ready
    if not force and not all([run_obj.archived_at, run_obj.delivered_at]):
        # not ready for clean up!
        log.warn("run not ready for clean up")
    else:
        for asset in run_obj.assets:
            if not asset.archive_type:
                asset.delete()
            else:
                asset.is_local = False

        run_dir = get_rundir(run_obj.case.name, run_obj)
        log.info("removing rundir: %s", run_dir)
        delete_dir(run_dir)
        run_obj.cleanedup_at = datetime.datetime.now()


def postpone(run_obj, time=datetime.timedelta(days=30)):
    """Postpone the automatic archival of analysis by X time."""
    run_obj.will_cleanup_at += time


def delete_dir(directory):
    directory_path = path(directory)
    if directory_path.exists():
        log.info("removing files under: %s", directory)
        directory_path.rmtree_p()
    else:
        log.debug("run directory not found: %s", directory)
