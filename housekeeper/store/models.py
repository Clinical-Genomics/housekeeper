# -*- coding: utf-8 -*-
from datetime import datetime
import json

import alchy
import bson
from path import path
from sqlalchemy import Column, ForeignKey, orm, types

from housekeeper.constants import PIPELINES


class JsonModel(alchy.ModelBase):

    def to_json(self, pretty=False):
        """Serialize Model to JSON."""
        kwargs = dict(indent=4, sort_keys=True) if pretty else dict()
        return json.dumps(self.to_dict(), default=bson.json_util.default,
                          **kwargs)


Model = alchy.make_declarative_base(Base=JsonModel)


class Metadata(Model):

    """Store information about the system."""

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, default=datetime.now)
    root = Column(types.String(128), nullable=False)

    @property
    def analyses_root(self):
        return path(self.root).joinpath('analyses')


class Analysis(Model):

    """Analysis record."""

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(128), unique=True)

    # metadata
    pipeline = Column(types.Enum(*PIPELINES))
    pipeline_version = Column(types.String(32))
    analyzed_at = Column(types.DateTime)
    delivered_at = Column(types.DateTime)

    # status (internal)
    status = Column(types.Enum('active', 'archived'))

    # assets
    assets = orm.relationship('Asset', cascade='all,delete', backref='analysis')
    samples = orm.relationship('Sample', cascade='all,delete', backref='analysis')


class Sample(Model):

    """Sample record."""

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(32), unique=True)

    # relationships
    analysis_id = Column(types.Integer, ForeignKey('analysis.id'),
                         nullable=False)
    assets = orm.relationship('Asset', backref='sample')


class Asset(Model):

    """Asset/file belonging to an analysis."""

    id = Column(types.Integer, primary_key=True)
    original_path = Column(types.String(128))
    path = Column(types.String(128), nullable=False, unique=True)
    checksum = Column(types.String(128))
    category = Column(types.String(32))
    to_archive = Column(types.Boolean)

    # relationships
    analysis_id = Column(types.Integer, ForeignKey('analysis.id'),
                         nullable=False)
    sample_id = Column(types.Integer, ForeignKey('sample.id'))
