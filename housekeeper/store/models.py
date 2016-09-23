# -*- coding: utf-8 -*-
from datetime import datetime
import json

import alchy
from path import path
from sqlalchemy import Column, ForeignKey, orm, types, UniqueConstraint

from housekeeper.constants import PIPELINES, ARCHIVE_TYPES


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


class Case(Model):
    """Store a permanent reference to a case."""

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(128), unique=True)
    created_at = Column(types.DateTime, default=datetime.now)

    runs = orm.relationship('AnalysisRun', cascade='all,delete',
                            backref='case', order_by='-AnalysisRun.id')

    @property
    def current(self):
        """Return the current (active) run."""
        return self.runs[0]


class AnalysisRun(Model):
    """Store information about a specific analysis run."""

    __table_args__ = (UniqueConstraint('case_id', 'analyzed_at',
                                       name='_uc_analysis_analyzed_at'),)

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, default=datetime.now)
    pipeline = Column(types.Enum(*PIPELINES))
    pipeline_version = Column(types.String(32))
    analyzed_at = Column(types.DateTime)
    compiled_at = Column(types.DateTime)
    delivered_at = Column(types.DateTime)
    archived_at = Column(types.DateTime)
    cleanedup_at = Column(types.DateTime)
    will_cleanup_at = Column(types.DateTime)

    case_id = Column(types.Integer, ForeignKey('case.id'), nullable=False)
    assets = orm.relationship('Asset', cascade='all,delete', backref='run')
    samples = orm.relationship('Sample', cascade='all,delete', backref='run')

    @property
    def cleanup_in(self):
        """Return number of days until archive happens."""
        time_diff = self.will_cleanup_at - datetime.today()
        return time_diff.days

    @property
    def sample_map(self):
        """Return dict of samples."""
        return {sample.name: sample for sample in self.samples}

    @property
    def analysis_date(self):
        """Date of the analysis run."""
        return self.analyzed_at.date()

    def to_dict(self, skip_samples=False):
        """Also include samples in the dict serialization."""
        analysis_dict = super(AnalysisRun, self).to_dict()
        analysis_dict['name'] = self.case.name
        if not skip_samples:
            sample_dicts = [sample.to_dict() for sample in self.samples]
            analysis_dict['samples'] = sample_dicts
        return analysis_dict


class Sample(Model):
    """Sample record."""

    __table_args__ = (UniqueConstraint('name', 'run_id',
                                       name='_uc_name_run_id'),)

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(32))

    run_id = Column(types.Integer, ForeignKey('analysis_run.id'),
                    nullable=False)
    assets = orm.relationship('Asset', backref='sample')


class Asset(Model):
    """Asset/file belonging to an analysis."""

    id = Column(types.Integer, primary_key=True)
    original_path = Column(types.Text)
    path = Column(types.String(256), nullable=False, unique=True)
    category = Column(types.String(32))
    archive_type = Column(types.Enum(*ARCHIVE_TYPES))
    is_local = Column(types.Boolean, default=True)
    checksum = Column(types.String(128))

    run_id = Column(types.Integer, ForeignKey('analysis_run.id'),
                    nullable=False)
    sample_id = Column(types.Integer, ForeignKey('sample.id'))

    def basename(self):
        return path(self.original_path).basename()
