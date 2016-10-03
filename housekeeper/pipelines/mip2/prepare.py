# -*- coding: utf-8 -*-
from __future__ import division
import logging

from housekeeper.exc import AnalysisNotFinishedError, UnsupportedVersionError
from housekeeper.pipelines.mip.meta import write_meta, build_meta

MULTIQC_SAMTOOLS = 'multiqc/multiqc_data/multiqc_samtools.txt'

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
    meta_output = build_meta(case_name, segments['family'], qcped_path,
                             version='v2.x')
    write_meta(meta_output, outdata_dir)


def validate(family):
    """Validate analysis."""
    run_status = family['AnalysisRunStatus']
    if run_status != 'Finished':
        log.warn("analysis not finished: %s", run_status)
        raise AnalysisNotFinishedError(run_status)

    mip_version = family.get('MIPVersion')
    if mip_version and mip_version.startswith('v3'):
        log.warn("pipeline too new: %s", mip_version)
        raise UnsupportedVersionError(mip_version)
