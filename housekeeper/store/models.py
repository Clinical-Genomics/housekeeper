# -*- coding: utf-8 -*-
from datetime import datetime
import json

import alchy
from path import Path
from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, orm, types, UniqueConstraint

from housekeeper.constants import PIPELINES, ARCHIVE_TYPES, EXTRA_STATUSES

SEQUENCERS = ('hiseqx', 'hiseq2500', 'hiseqHO', 'miseq', 'nextseq')
SAMPLE_CATEGORIES = ('wgs', 'wes', 'tga', 'wgs-ext', 'wes-ext', 'tga-ext')


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


class SampleRunLink(Model):

    """Link between UniqueSample and AnalysisRun."""

    __table_args__ = (
        UniqueConstraint('sample_id', 'run_id', name='_sample_run_uc'),
    )

    id = Column(types.Integer, primary_key=True)
    sample_id = Column(ForeignKey('sample.id'), nullable=False)
    run_id = Column(ForeignKey('analysis_run.id'), nullable=False)


class Sample(Model):

    """Store unique reference to a sample."""

    id = Column(types.Integer, primary_key=True)
    lims_id = Column(types.String(32), nullable=False, unique=True)
    case_id = Column(ForeignKey('case.id'))
    priority = Column(types.Boolean, default=False)
    _flowcells = Column(types.Text)
    category = Column(types.Enum(*SAMPLE_CATEGORIES))

    created_at = Column(types.DateTime, default=datetime.now)
    received_at = Column(types.DateTime)
    sequenced_at = Column(types.DateTime)
    confirmed_at = Column(types.DateTime)

    assets = orm.relationship('Asset', backref='sample', cascade='all,delete')
    runs = orm.relationship('AnalysisRun', secondary='sample_run_link',
                            back_populates='samples')

    @property
    def flowcells(self):
        """Return a list of flowcells."""
        flowcell_list = self._flowcells.split(',') if self._flowcells else []
        return flowcell_list

    @flowcells.setter
    def flowcells(self, flowcell_list):
        self._flowcells = ','.join(flowcell_list) if flowcell_list else None


class Case(Model):

    """Store a permanent reference to a case."""

    id = Column(types.Integer, primary_key=True)
    name = Column(types.String(128), unique=True, nullable=False)
    customer = Column(types.String(32), nullable=False)
    family_id = Column(types.String(128), nullable=False)
    created_at = Column(types.DateTime, default=datetime.now)
    is_onhold = Column(types.Boolean, default=False)
    comment = Column(types.Text)
    is_started = Column(types.Boolean, default=False)
    is_manual = Column(types.Boolean)
    rerun_requested = Column(types.Boolean, default=False)

    runs = orm.relationship('AnalysisRun', cascade='all,delete',
                            backref='case', order_by='-AnalysisRun.id')
    samples = orm.relationship('Sample', backref='case', cascade='all,delete')

    @property
    def has_priority(self):
        """Check if related sample is priority."""
        return any(sample.priority for sample in self.samples)

    @property
    def current(self):
        """Return the current (active) run."""
        if self.runs:
            return self.runs[0]
        else:
            return None


class AnalysisRun(Model):

    """Store information about a specific analysis run."""

    __table_args__ = (
        UniqueConstraint('case_id', 'analyzed_at', name='_uc_case_analyzed'),
    )

    id = Column(types.Integer, primary_key=True)
    created_at = Column(types.DateTime, default=datetime.now)
    pipeline = Column(types.Enum(*PIPELINES))
    pipeline_version = Column(types.String(32))
    reference_genome = Column(types.String(64))
    # keep track of a date if the cases is requested to be rerun
    requested_at = Column(types.DateTime)
    analyzed_at = Column(types.DateTime)
    compiled_at = Column(types.DateTime)
    delivered_at = Column(types.DateTime)
    answeredout_at = Column(types.DateTime)
    archived_at = Column(types.DateTime)
    cleanedup_at = Column(types.DateTime)
    will_cleanup_at = Column(types.DateTime)

    case_id = Column(ForeignKey(Case.id), nullable=False)
    assets = orm.relationship('Asset', cascade='all,delete', backref='run')
    samples = orm.relationship('Sample', secondary='sample_run_link',
                               back_populates='runs')
    extra = orm.relationship('ExtraRunData', backref='run',
                             cascade='all,delete', uselist=False)

    @property
    def cleanup_in(self):
        """Return number of days until archive happens."""
        time_diff = self.will_cleanup_at - datetime.today()
        return time_diff.days

    @property
    def sample_map(self):
        """Return dict of samples."""
        return {sample.lims_id: sample for sample in self.samples}

    @property
    def analysis_date(self):
        """Date of the analysis run."""
        return self.analyzed_at.date()

    def suggested_delivery(self):
        """Suggest date for delivery based on upload dates."""
        uploads = []
        for column in EXTRA_STATUSES:
            column_key = "{}_date".format(column)
            upload_date = getattr(self.extra, column_key)
            if upload_date:
                uploads.append(upload_date)
        latest_date = max(uploads)
        return latest_date.date() if latest_date else None

    def to_dict(self, skip_samples=False):
        """Also include samples in the dict serialization."""
        analysis_dict = super(AnalysisRun, self).to_dict()
        analysis_dict['name'] = self.case.name
        if not skip_samples:
            sample_dicts = [sample.to_dict() for sample in self.samples]
            analysis_dict['samples'] = sample_dicts
        return analysis_dict


class Asset(Model):

    """Asset/file belonging to an analysis."""

    id = Column(types.Integer, primary_key=True)
    original_path = Column(types.Text)
    path = Column(types.String(256), nullable=False, unique=True)
    category = Column(types.String(32))
    archive_type = Column(types.Enum(*ARCHIVE_TYPES))
    is_local = Column(types.Boolean, default=True)
    checksum = Column(types.String(128))

    run_id = Column(ForeignKey(AnalysisRun.id), nullable=False)
    sample_id = Column(ForeignKey('sample.id'))

    def basename(self):
        return Path(self.original_path).basename()


class User(Model, UserMixin):
    id = Column(types.Integer, primary_key=True)
    google_id = Column(types.String(128), unique=True)
    email = Column(types.String(128), unique=True)
    name = Column(types.String(128))
    avatar = Column(types.Text)

    @property
    def first_name(self):
        """First part of name."""
        return self.name.split(' ')[0]


class ExtraRunData(Model):

    """Store custom extra fields related to a run."""

    id = Column(types.Integer, primary_key=True)
    run_id = Column(ForeignKey('analysis_run.id'), nullable=False, unique=True)

    # custom dates
    coverage_date = Column(types.DateTime)
    frequency_date = Column(types.DateTime)
    genotype_date = Column(types.DateTime)
    visualizer_date = Column(types.DateTime)
    rawdata_date = Column(types.DateTime)
    qc_date = Column(types.DateTime)
