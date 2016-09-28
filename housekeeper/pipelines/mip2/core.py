# -*- coding: utf-8 -*-
import logging

from housekeeper.pipelines.mip.build import build_analysis, build_asset
from housekeeper.pipelines.mip.parse import prepare_inputs, parse_references
from .prepare import prepare_run

log = logging.getLogger(__name__)


def parse(config_data, reference_data, force=False):
    """Parse MIP analysis output."""
    # 1. parse segments of input data
    segments = prepare_inputs(config_data)
    # 2. post-process the output a bit
    prepare_run(segments, force=force)
    # 3. build the records
    new_objs = build_analysis(segments, version='v2.x')
    # 4. parse references
    config_path = config_data['writeConfigFile']
    new_refs = parse_references(reference_data, segments=segments)
    # 5. build assets from references + link to new records
    for ref_data in new_refs:
        new_asset = build_asset(ref_data['path'], ref_data['reference'])
        if ref_data['reference'].get('sample'):
            sample_obj = new_objs['run'].sample_map[ref_data['sample']]
            sample_obj.assets.append(new_asset)
        new_objs['run'].assets.append(new_asset)

    return new_objs
