# -*- coding: utf-8 -*-
from __future__ import division
import logging

from housekeeper.exc import AnalysisNotFinishedError, UnsupportedVersionError
from housekeeper.pipelines.mip.meta import build_meta, write_meta
from housekeeper.pipelines.mip.prepare import modify_qcmetrics

log = logging.getLogger(__name__)

MULTIQC_SAMTOOLS = 'multiqc/multiqc_data/multiqc_samtools_stats.txt'


def prepare_run(segments, force=False):
    """Prepare MIP output."""
    if not force:
        validate(segments['family'])

    outdata_dir = segments['config']['outDataDir']
    qcped_path = segments['family']['PedigreeFileAnalysis']['Path']
    fam_key = segments['config']['familyID']
    customer = segments['pedigree']['customer']
    case_name = "{}-{}".format(customer, fam_key)
    meta_output = build_meta(case_name, segments['family'], qcped_path)
    write_meta(meta_output, outdata_dir)

    qcmetrics_path = (segments['family']['Program']['QCCollect']
                              ['QCCollectMetricsFile']['Path'])
    sample_ids = segments['config']['sampleIDs']
    modify_qcmetrics(outdata_dir, qcmetrics_path, sample_ids,
                     multiqc_samtools=MULTIQC_SAMTOOLS)


def validate(family):
    """Validate analysis."""
    run_status = family['AnalysisRunStatus']
    if run_status != 'Finished':
        raise AnalysisNotFinishedError(run_status)

    version = family['MIPVersion']
    if not version.startswith('v4'):
        raise UnsupportedVersionError(version)
