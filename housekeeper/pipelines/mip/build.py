# -*- coding: utf-8 -*-
from __future__ import division
import logging

from path import path

from housekeeper.pipelines.general.add import analysis as general_analysis
from housekeeper.store import Asset

log = logging.getLogger(__name__)


def build_analysis(segments, version=None, customer=None):
    """Prepare info for a MIP analysis."""
    fam_key = segments['config']['familyID']
    version = version if version else segments['family']['MIPVersion']
    analyzed_at = segments['family']['AnalysisDate']
    sample_ids = segments['config']['sampleIDs']
    customer = customer or segments['family']['InstanceTag'][0]
    name = "{}-{}".format(customer, fam_key)
    log.debug("build new analysis record: %s", name)
    new_run = general_analysis('mip', version, analyzed_at)
    return {'case': name, 'run': new_run, 'samples': sample_ids}


def build_asset(asset_path, reference):
    """Build Asset record from reference data."""
    abs_path = path(asset_path).abspath()
    new_asset = Asset(original_path=abs_path, category=reference['category'],
                      archive_type=reference.get('archive_type'))
    return new_asset
