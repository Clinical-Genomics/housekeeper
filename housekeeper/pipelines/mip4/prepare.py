# -*- coding: utf-8 -*-
from __future__ import division
import logging

from path import Path
import yaml

from housekeeper.exc import AnalysisNotFinishedError, UnsupportedVersionError
from housekeeper.pipelines.mip.meta import write_meta
from .meta import build_meta

log = logging.getLogger(__name__)


def prepare_run(segments, force=False):
    """Prepare MIP output."""
    if not force:
        validate(segments['family'])

    outdata_dir = segments['config']['outdata_dir']
    fam_key = segments['config']['family_id']
    customer = segments['pedigree']['owner']
    case_name = "{}-{}".format(customer, fam_key)
    meta_output = build_meta(case_name, segments)
    write_meta(meta_output, outdata_dir)
    qcmetrics_path = (segments['family']['program']['qccollect']
                              ['qccollect_metrics_file']['path'])
    modify_qcmetrics(outdata_dir, qcmetrics_path)


def validate(family):
    """Validate analysis."""
    run_status = family['analysisrunstatus']
    if run_status != 'finished':
        raise AnalysisNotFinishedError(run_status)

    version = family['mip_version']
    if not version.startswith('v4'):
        raise UnsupportedVersionError(version)


def modify_qcmetrics(outdata_dir, qcmetrics_path):
    """Summarize some stats on sample level."""
    with open(qcmetrics_path, 'r') as in_handle:
        qc_data = yaml.load(in_handle)

    for sample_id, values in qc_data['sample'].items():
        # extract data dicts
        datas = [data for level_id, data in values.items() if
                 level_id[-6:-1] == '.lane']
        reads, mapped = 0, 0
        for data in datas:
            reads += data['bamstats']['raw_total_sequences']
            mapped += data['bamstats']['reads_mapped']

        values['reads'] = reads
        values['reads_mapped'] = mapped
        values['reads_mapped_rate'] = mapped / reads

    new_qcmetrics = Path(qcmetrics_path.replace('.yaml', '.mod.yaml'))
    log.info("create updated qc metrics: %s", new_qcmetrics)
    with new_qcmetrics.open('w') as out_handle:
        yaml.safe_dump(qc_data, stream=out_handle, default_flow_style=False)
