# -*- coding: utf-8 -*-
from __future__ import division
import logging
import os

from housekeeper.exc import AnalysisNotFinishedError
from housekeeper.pipelines.mip.meta import write_meta, build_meta

log = logging.getLogger(__name__)


def prepare_run(segments, force=False):
    """Prepare MIP output."""
    if not force:
        validate(segments['family'])

    fam_key = segments['config']['familyID']
    mip_version = segments['family'].get('MIPVersion', 'v2.x')
    outdata_dir = segments['family']['ArchivePath']
    qcped_path = os.path.join(outdata_dir, fam_key, 'qc_pedigree.yaml')
    customer = segments['family']['InstanceTag'][0]
    case_name = "{}-{}".format(customer, fam_key)
    meta_output = build_meta(case_name, segments['family'], qcped_path,
                             version=mip_version, strict=False)
    write_meta(meta_output, outdata_dir)


def validate(family):
    """Validate analysis."""
    run_status = family['AnalysisRunStatus']
    if run_status != 'Archived':
        raise AnalysisNotFinishedError(run_status)
