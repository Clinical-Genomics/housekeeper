# -*- coding: utf-8 -*-
import logging

from path import path

from housekeeper.exc import MissingFileError
from .build import build_analysis, build_asset
from .parse import prepare_inputs, parse_references
from .prepare import prepare_run

log = logging.getLogger(__name__)


def build_assets(new_references, force=False):
    """Build assets from references."""
    for ref_data in new_references:
        log.debug("working on: %s", ref_data['reference']['category'])
        if not path(ref_data['path']).exists():
            is_required = ref_data['reference'].get('required', True)
            if force or not is_required:
                log.warn("skipping asset: %s", ref_data['path'])
                continue
            else:
                raise MissingFileError(ref_data['path'])

        new_asset = build_asset(ref_data['path'], ref_data['reference'])
        yield new_asset, ref_data.get('sample')


def link_asset(run_obj, new_asset, sample=None):
    if sample:
        run_obj.sample_map[sample].assets.append(new_asset)
    run_obj.assets.append(new_asset)


def parse_mip(config_data, reference_data, force=False):
    """Parse MIP analysis output."""
    # 1. parse segments of input data
    segments = prepare_inputs(config_data)
    # 2. post-process the output a bit
    prepare_run(segments, force=force)
    # 3. build the records
    new_data = build_analysis(segments)
    # 4. parse references
    new_refs = parse_references(reference_data, segments)
    # 5. build assets from references + link to new records
    new_assets = build_assets(new_refs, force=force)
    return {
        'case': new_data['case'],
        'samples': new_data['samples'],
        'run': new_data['run'],
        'assets': new_assets,
    }
