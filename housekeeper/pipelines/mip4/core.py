# -*- coding: utf-8 -*-
import logging

from housekeeper.pipelines.general.add import analysis as general_analysis
from housekeeper.pipelines.mip.parse import parse_references
from housekeeper.pipelines.mip.core import build_assets
from .parse import prepare_inputs
from .prepare import prepare_run

log = logging.getLogger(__name__)


def parse_mip4(config_data, reference_data, force=False):
    """Parse MIP analysis output."""
    # 1. parse segments of input data
    segments = prepare_inputs(config_data)
    # 2. post-process the output a bit
    prepare_run(segments, force=force)
    # 3. build the records
    new_data = build_analysis(segments)
    # 4. parse references
    new_refs = parse_references(reference_data, segments=segments)
    # 5. build assets from references + link to new records
    new_assets = build_assets(new_refs)
    return {
        'case': new_data['case'],
        'samples': new_data['samples'],
        'run': new_data['run'],
        'assets': new_assets,
    }


def build_analysis(segments):
    """Prepare info for a MIP analysis."""
    version = segments['family']['mip_version']
    analyzed_at = segments['family']['analysis_date']
    sample_ids = segments['config']['sample_ids']
    customer = segments['pedigree']['owner']
    name = "{}-{}".format(customer, segments['config']['family_id'])
    log.debug("build new analysis record: %s", name)
    new_run = general_analysis('mip', version, analyzed_at)
    return {'case': name, 'run': new_run, 'samples': sample_ids}
