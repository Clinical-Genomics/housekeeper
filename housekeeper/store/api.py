# -*- coding: utf-8 -*-
import datetime
import logging

from alchy import Manager
from path import Path
import sqlalchemy as sqa

from housekeeper.constants import EXTRA_STATUSES
from .models import AnalysisRun, Asset, Case, Model, Sample, ExtraRunData
from .utils import get_rundir

log = logging.getLogger(__name__)
DATE_2017 = datetime.datetime(2017, 1, 1)


def manager(db_uri):
    log.debug('open connection to database: %s', db_uri)
    db = Manager(config=dict(SQLALCHEMY_DATABASE_URI=db_uri), Model=Model,
                 session_options=dict(autoflush=False))
    return db


def assets(case_name=None, sample=None, category=None, run_id=None):
    """Get files from the database."""
    query = Asset.query
    if run_id:
        query = query.filter_by(run_id=run_id)
    elif case_name:
        query = (query.join(Asset.run, AnalysisRun.case)
                      .filter(Case.name == case_name))
    if sample:
        query = query.join(Asset.sample).filter(Sample.lims_id == sample)
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


def samples(query_str=None, status_to=None, customer=None, family_id=None):
    """Get samples from the database."""
    query = (Sample.query.join(Sample.case)
                         .filter(Case.is_manual == None)
                         .order_by(Sample.priority.desc(), Sample.received_at))
    if query_str:
        query = query.filter(Sample.lims_id.like("%{}%".format(query_str)))

    if status_to == 'sequence':
        query = query.filter(Sample.received_at > datetime.date(2017, 1, 1),
                             Sample.sequenced_at == None)
    elif status_to == 'confirm':
        query = query.filter(Sample.sequenced_at != None, Sample.confirmed_at == None)
    elif status_to == 'receive':
        query = query.filter(Sample.received_at == None, Sample.sequenced_at == None)

    if customer:
        query = query.filter_by(customer=customer)
    if family_id:
        query = query.filter_by(family_id=family_id)

    return query


def sample(lims_id):
    """Get sample from the database."""
    sample_obj = Sample.query.filter_by(lims_id=lims_id).first()
    return sample_obj


def cases(query_str=None, missing=None, version=None, onhold=None):
    """Get multiple cases from the database."""
    query = Case.query.filter(Case.is_manual == None).order_by(Case.created_at)

    if missing == 'analyzed':
        not_analyzed = ((Sample.sequenced_at > datetime.date(2017, 1, 1)) &
                        (AnalysisRun.analyzed_at == None))
        query = (query.outerjoin(Case.runs)
                      .join(Case.samples)
                      .filter(not_analyzed | Case.rerun_requested))
    elif missing == 'delivered':
        query = (query.join(Case.runs)
                      .filter(AnalysisRun.analyzed_at != None,
                              AnalysisRun.delivered_at == None,
                              AnalysisRun.pipeline_version.like("%v4.%")))
    elif missing == 'archived':
        query = (query.join(Case.runs)
                      .filter(AnalysisRun.archived_at == None))
    elif missing == 'answeredout':
        query = (query.join(Case.runs)
                      .filter(AnalysisRun.delivered_at != None,
                              AnalysisRun.answeredout_at == None))
    elif missing == 'cleanedup':
        today = datetime.datetime.today()
        query = (query.join(Case.runs)
                      .filter(AnalysisRun.will_cleanup_at < today))
    elif missing in EXTRA_STATUSES:
        date_field = getattr(ExtraRunData, "{}_date".format(missing))
        query = (query.join(Case.runs, AnalysisRun.extra)
                      .filter(AnalysisRun.analyzed_at != None,
                              date_field == None))
    if version:
        like_str = "{}%".format(version)
        query = (query.join(Case.runs)
                      .filter(AnalysisRun.pipeline_version.like(like_str)))
    if query_str:
        query = query.filter(Case.name.like("%{}%".format(query_str)))

    if onhold is not None:
        query = query.filter(Case.is_onhold == onhold)
    return query


def runs(case_name=None, run_date=None, since=None, before=None, after=None,
         archived=None, compiled=None, cleaned=None, to_clean=None):
    """Get runs for a case from the database.

    Args:
        case_name (str): the unique name of the case

    Returns:
        Query: all runs for the case
    """
    run_query = AnalysisRun.query
    if run_date:
        delta = datetime.timedelta(days=1)
        next_day = run_date + delta
        condition = AnalysisRun.analyzed_at.between(run_date, next_day)
        run_query = run_query.filter(condition)

    order = AnalysisRun.analyzed_at.desc()
    if after:
        since = after
    if since:
        order = AnalysisRun.analyzed_at.desc()
        run_query = run_query.filter(AnalysisRun.analyzed_at > since)
    if before:
        order = AnalysisRun.analyzed_at
        run_query = run_query.filter(AnalysisRun.analyzed_at < before)

    if to_clean:
        today = datetime.datetime.today()
        run_query = run_query.filter(AnalysisRun.archived_at != None,
                                     AnalysisRun.cleanedup_at == None,
                                     AnalysisRun.will_cleanup_at < today)
    else:
        if archived:
            if archived is True:
                run_query = run_query.filter(AnalysisRun.archived_at != None)
            else:
                run_query = run_query.filter(AnalysisRun.archived_at == None)
        if compiled is not None:
            if compiled is True:
                run_query = run_query.filter(AnalysisRun.compiled_at != None)
            else:
                run_query = run_query.filter(AnalysisRun.compiled_at == None)
        if cleaned:
            if cleaned is True:
                run_query = run_query.filter(AnalysisRun.cleanedup_at != None)
            else:
                run_query = run_query.filter(AnalysisRun.cleanedup_at == None)
    if case_name:
        run_query = (run_query.join(AnalysisRun.case)
                              .filter(Case.name == case_name))
    return run_query.order_by(order)


def delete(root_path, run_obj):
    """Delete an analysis run along with related files on the system.

    Args:
        run_obj (AnalysisRun): the analysis run to delete
    """
    run_dir = get_rundir(root_path, run_obj.case.name, run_obj)
    delete_dir(run_dir)
    run_obj.delete()


def delete_asset(asset_obj):
    """Delete an asset completely from the database."""
    if asset_obj.is_local:
        Path(asset_obj.path).remove_p()
    asset_obj.delete()


def clean_up(root_path, run_obj, force=False, untagged_only=False):
    """Clean up files for an analysis."""
    # check if run is ready
    if not force and not all([run_obj.archived_at, run_obj.delivered_at]):
        # not ready for clean up!
        log.warn("run not ready for clean up")
    else:
        for asset in run_obj.assets:
            if not asset.archive_type:
                asset.delete()
                delete_file(asset.path)
            else:
                if not untagged_only:
                    asset.is_local = False

        if not untagged_only:
            run_dir = get_rundir(root_path, run_obj.case.name, run_obj)
            log.info("removing rundir: %s", run_dir)
            delete_dir(run_dir)
            run_obj.cleanedup_at = datetime.datetime.now()


def postpone(run_obj, time=datetime.timedelta(days=30)):
    """Postpone the automatic archival of analysis by X time."""
    run_obj.will_cleanup_at += time


def delete_file(filename):
    file_path = Path(filename)
    if file_path.exists():
        log.info("removing file : %s", filename)
        file_path.remove_p()
    else:
        log.debug("asset not found: %s", filename)


def delete_dir(directory):
    directory_path = Path(directory)
    if directory_path.exists():
        log.info("removing files under: %s", directory)
        directory_path.rmtree_p()
    else:
        log.debug("run directory not found: %s", directory)


def add_asset(run_obj, asset_path, category, archive_type=None, sample=None):
    """Link an asset to a run."""
    abs_path = Path(asset_path).abspath()
    new_asset = Asset(original_path=abs_path, category=category,
                      archive_type=archive_type)
    new_asset.sample = sample
    return new_asset


def sha1(asset_path):
    """Retrieves the sha1sum from an asset"""
    abs_path = Path(asset_path).abspath()
    query = Asset.query
    checksum = query.filter(Asset.original_path == abs_path).first().checksum

    return checksum


def to_analyzed(session, category, limit=50):
    """Calculate times it takes to analyze a sample."""
    query = (session.query(Sample.lims_id, Sample.received_at, AnalysisRun.analyzed_at)
                    .join(Sample.runs)
                    .filter(Sample.category == category, Sample.received_at > DATE_2017)
                    .order_by(Sample.received_at.desc())
                    .limit(limit))
    diffs = [{
        'name': item[0],
        'y': (item[2] - item[1]).days
    } for item in query]
    return diffs


def to_sequenced(session, category, limit=50):
    """Calculate time it takes to sequence samples."""
    day_diff = sqa.func.TIMESTAMPDIFF(sqa.text('DAY'), Sample.received_at, Sample.sequenced_at)
    query = (session.query(Sample.lims_id.label('name'), day_diff.label('y'))
                    .filter(Sample.category == category, Sample.received_at > DATE_2017)
                    .order_by(Sample.received_at.desc())
                    .limit(limit))
    diffs = [{'name': sample.name, 'y': sample.y} for sample in query]
    return diffs
