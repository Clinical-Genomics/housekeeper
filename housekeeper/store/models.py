# -*- coding: utf-8 -*-
from datetime import datetime
import json

import alchy
from path import path
from sqlalchemy import Column, ForeignKey, orm, types, UniqueConstraint

from housekeeper.constants import PIPELINES


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError('Type not serializable')


class JsonModel(alchy.ModelBase):

    def to_json(self, pretty=False):
        """Serialize Model to JSON."""
        kwargs = dict(indent=4, sort_keys=True) if pretty else dict()
        return json.dumps(self.to_dict(), default=json_serial, **kwargs)


Model = alchy.make_declarative_base(Base=JsonModel)


class Metadata(Model):
    """Store information about the system."""

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, default=datetime.now)
    root = Column(types.String(128), nullable=False)

    @property
    def root_path(self):
        return path(self.root)


class AnalysisRun(Model):
    """Store information about a specific analysis run."""

    __tablename__ = 'analysis_run'
    __table_args__ = (UniqueConstraint('analysis', 'analyzed_at',
                                       name='_uc_analysis_analyzed_at'),)

    id = Column(types.Integer, primary_key=True)
    pipeline_version = Column(types.String(32))
    created_at = Column(types.DateTime, default=datetime.now)
    analyzed_at = Column(types.DateTime)
    delivered_at = Column(types.DateTime)
    archived_at = Column(types.DateTime)
    # status (internal)
    status = Column(types.Enum('active', 'archived'))
    analysis = Column(types.String(128))


class Analysis(Model):
    """Analysis record."""

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(128), unique=True)
    created_at = Column(types.DateTime, default=datetime.now)

    # metadata
    pipeline = Column(types.Enum(*PIPELINES))
    will_archive_at = Column(types.DateTime)

    # assets
    assets = orm.relationship('Asset', cascade='all,delete', backref='analysis')
    samples = orm.relationship('Sample', cascade='all,delete', backref='analysis')

    def to_dict(self, skip_samples=False):
        """Also include samples in the dict serialization."""
        analysis_dict = super(Analysis, self).to_dict()
        if not skip_samples:
            sample_dicts = [sample.to_dict() for sample in self.samples]
            analysis_dict['samples'] = sample_dicts
        return analysis_dict


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
    original_path = Column(types.Text)
    path = Column(types.String(256), nullable=False, unique=True)
    checksum = Column(types.String(128))
    category = Column(types.String(32))
    to_archive = Column(types.Boolean)

    # relationships
    analysis_id = Column(types.Integer, ForeignKey('analysis.id'),
                         nullable=False)
    sample_id = Column(types.Integer, ForeignKey('sample.id'))
