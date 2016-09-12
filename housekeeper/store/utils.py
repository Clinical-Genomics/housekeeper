# -*- coding: utf-8 -*-
import logging

from alchy import Manager

from .models import Model, Asset, Analysis, Case, Sample

log = logging.getLogger(__name__)


def get_manager(db_uri):
    log.debug('open connection to database: %s', db_uri)
    db = Manager(config=dict(SQLALCHEMY_DATABASE_URI=db_uri), Model=Model,
                 session_options=dict(autoflush=False))
    return db


def get_assets(analysis=None, sample=None, category=None):
    """Get files from the database."""
    query = Asset.query
    if analysis:
        query = (query.join(Asset.analysis, Analysis.case)
                      .filter(Case.name == analysis))
    if sample:
        query = query.join(Asset.sample).filter(Sample.name == sample)
    if category:
        query = query.filter(Asset.category == category)
    return query
