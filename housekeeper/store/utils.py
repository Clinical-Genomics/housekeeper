# -*- coding: utf-8 -*-
import logging

from alchy import Manager

from .models import Model, Asset, AnalysisRun, Case, Sample, Metadata

log = logging.getLogger(__name__)


def get_manager(db_uri):
    log.debug('open connection to database: %s', db_uri)
    db = Manager(config=dict(SQLALCHEMY_DATABASE_URI=db_uri), Model=Model,
                 session_options=dict(autoflush=False))
    return db


def get_assets(case_name=None, sample=None, category=None):
    """Get files from the database."""
    query = Asset.query
    if case_name:
        query = (query.join(Asset.analysis, AnalysisRun.case)
                      .filter(Case.name == case_name))
    if sample:
        query = query.join(Asset.sample).filter(Sample.name == sample)
    if category:
        query = query.filter(Asset.category == category)
    return query


def get_rundir(case_name, run):
    """Return path to run root dir."""
    meta = Metadata.query.first()
    root = meta.root_path.joinpath(case_name, run.analysis_date.isoformat())
    return root
