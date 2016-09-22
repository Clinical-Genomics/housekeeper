# -*- coding: utf-8 -*-
from __future__ import division
import logging

from path import path

from housekeeper.pipelines.general.add import analysis as general_analysis
from housekeeper.store import Asset

log = logging.getLogger(__name__)


def build_analysis(segments):
    """Prepare info for a MIP analysis."""
    fam_key = segments['config']['familyID']
    version = segments['family']['MIPVersion']
    analyzed_at = segments['family']['AnalysisDate']
    sample_ids = segments['config']['sampleIDs']
    customer = segments['family']['InstanceTag'][0]
    name = "{}-{}".format(customer, fam_key)
    log.debug("build new analysis record: %s", name)
    new_objs = general_analysis(name, 'mip', version, analyzed_at, sample_ids)
    return new_objs


def build_asset(asset_path, reference):
    """Build Asset record from reference data."""
    abs_path = path(asset_path).abspath()
    new_asset = Asset(original_path=abs_path, category=reference['category'],
                      archive_type=reference.get('archive_type'))
    return new_asset
