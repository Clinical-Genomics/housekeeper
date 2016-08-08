# -*- coding: utf-8 -*-
import logging

from alchy import Manager

from .models import Model, Asset, Analysis, Sample

log = logging.getLogger(__name__)


def get_manager(uri):
    log.debug('open connection to database: %s', uri)
    db = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return db


def get_assets(analysis=None, sample=None, category=None):
    """Get files from the database."""
    query = Asset.query
    if analysis:
        query = query.join(Asset.analysis).filter(Analysis.name == analysis)
    if sample:
        query = query.join(Asset.sample).filter(Sample.name == sample)
    if category:
        query = query.filter(Asset.category == category)
    return query
