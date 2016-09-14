# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from path import path

from housekeeper.store import AnalysisRun, Case, Sample, Asset
from housekeeper.constants import TIME_TO_CLEANUP

log = logging.getLogger(__name__)


def analysis(name, pipeline, version, analyzed_at, samples=None):
    """Store information about a general analysis run.

    This is the most low level implementation of how to store files from an
    analysis.
    """
    new_case = Case(name=name)
    new_run = AnalysisRun(pipeline=pipeline, pipeline_version=version,
                          analyzed_at=analyzed_at)

    # set the future date for archiving
    new_run.will_cleanup_at = datetime.now() + TIME_TO_CLEANUP

    for sample_id in (samples or []):
        new_run.samples.append(Sample(name=sample_id))
    return {'case': new_case, 'run': new_run}


def asset(asset_path, category, archive_type=None):
    """Store an analysis file."""
    abs_path = path(asset_path).abspath()
    log.debug("calculate checksum for: %s", abs_path)
    new_asset = Asset(original_path=abs_path, category=category,
                      archive_type=archive_type)
    return new_asset
