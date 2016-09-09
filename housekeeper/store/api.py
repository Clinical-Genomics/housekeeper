# -*- coding: utf-8 -*-
import datetime
import logging

from path import path

from .models import Analysis, AnalysisRun, Case, Metadata

log = logging.getLogger(__name__)


def case(name):
    """Get a case from the database.

    Args:
        name (str): the unique name of the analysis

    Returns:
        Case or None: the case or None if not found
    """
    case_obj = Case.query.filter_by(name=name).first()
    return case_obj


def analysis(name):
    """Get an analysis from the database.

    Args:
        name (str): the unique name of the case

    Returns:
        Analysis or None: the analysis or None if not found
    """
    # 'name' is a unique column so it will always return 1 or 0 records
    analysis_obj = (Analysis.query.join(Analysis.case)
                            .filter(Case.name == name)
                            .first())
    return analysis_obj


def runs(name):
    """Get runs for a case from the database.

    Args:
        name (str): the unique name of the case

    Returns:
        Query: all runs for the case
    """
    run_query = (AnalysisRun.query.join(AnalysisRun.case)
                            .filter(Case.name == name)
                            .order_by(AnalysisRun.created_at.desc()))
    return run_query


def delete(analysis_obj):
    """Delete an analysis along with related files on the system.

    Args:
        analysis_obj (Analysis): the analysis to delete
    """
    analysis_obj.delete()
    meta = Metadata.query.first()
    analysis_dir = meta.root_path.joinpath(analysis_obj.case.name)
    log.info("removing files under: %s", analysis_dir)
    analysis_dir.rmtree_p()


def archive(analysis_obj):
    """Archive an analysis and remove files not marked for archival.

    Args:
        analysis_obj (Analysis): the analysis to delete
    """
    # remove all files that aren't marked for archive
    for asset in analysis_obj.assets:
        if not asset.to_archive:
            path(asset.path).remove()
            asset.delete()

    # marked the case as "archived"
    analysis_obj.status = 'archived'


def postpone(analysis_obj, time=datetime.timedelta(days=30)):
    """Postpone the automatic archival of analysis by X time."""
    analysis_obj.will_archive_at += time
