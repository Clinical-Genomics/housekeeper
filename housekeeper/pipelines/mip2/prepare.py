# -*- coding: utf-8 -*-
from __future__ import division
import logging

from housekeeper.exc import AnalysisNotFinishedError, UnsupportedVersionError
from housekeeper.pipelines.mip.meta import write_meta, build_meta

log = logging.getLogger(__name__)


def prepare_run(segments, force=False):
    """Prepare MIP output."""
    if not force:
        validate(segments['family'])

    outdata_dir = segments['config']['outDataDir']
    qcped_path = segments['family']['PedigreeFileAnalysis']['Path']
    fam_key = segments['config']['familyID']
    customer = segments['family']['InstanceTag'][0]
    case_name = "{}-{}".format(customer, fam_key)
    mip_version = segments['family'].get('MIPVersion', 'v2.x')
    meta_output = build_meta(case_name, segments['family'], qcped_path,
                             version=mip_version, strict=False)
    write_meta(meta_output, outdata_dir)


def validate(family):
    """Validate analysis."""
    run_status = family['AnalysisRunStatus']
    if run_status != 'Finished':
        raise AnalysisNotFinishedError(run_status)

    mip_version = family.get('MIPVersion')
    if mip_version and mip_version.startswith('v3'):
        raise UnsupportedVersionError(mip_version)
