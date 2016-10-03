# -*- coding: utf-8 -*-
import logging

from housekeeper.pipelines.mip.build import build_analysis
from housekeeper.pipelines.mip.parse import prepare_inputs, parse_references
from housekeeper.pipelines.mip.core import build_assets, link_asset
from .prepare import prepare_run

log = logging.getLogger(__name__)


def parse(config_data, reference_data, force=False):
    """Parse MIP analysis output."""
    # 1. parse segments of input data
    segments = prepare_inputs(config_data)
    # 2. post-process the output a bit
    prepare_run(segments, force=force)
    # 3. build the records
    mip_version = segments['family'].get('MIPVersion', 'v2.x')
    new_objs = build_analysis(segments, version=mip_version)
    # 4. parse references
    new_refs = parse_references(reference_data, segments=segments)
    # 5. build assets from references + link to new records
    new_assets = build_assets(new_refs)
    for new_asset, sample in new_assets:
        link_asset(new_objs['run'], new_asset, sample=sample)
    return new_objs
