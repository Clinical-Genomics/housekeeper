# -*- coding: utf-8 -*-
from __future__ import division
import csv
import logging
import re

from path import path
import yaml

from housekeeper.exc import AnalysisNotFinishedError, UnsupportedVersionError
from .meta import build_meta, write_meta

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
    meta_output = build_meta(case_name, segments['family'], qcped_path)
    write_meta(meta_output, outdata_dir)

    qcmetrics_path = (segments['family']['Program']['QCCollect']
                              ['QCCollectMetricsFile']['Path'])
    sample_ids = segments['config']['sampleIDs']
    modify_qcmetrics(outdata_dir, qcmetrics_path, sample_ids)


def validate(family):
    """Validate analysis."""
    run_status = family['AnalysisRunStatus']
    if run_status != 'Finished':
        raise AnalysisNotFinishedError(run_status)

    version = family['MIPVersion']
    if not version.startswith('v3'):
        raise UnsupportedVersionError(version)


def modify_qcmetrics(outdata_dir, qcmetrics_path, sample_ids,
                     multiqc_samtools=MULTIQC_SAMTOOLS):
    # multiqc outputs
    qc_samples = {}
    for sample_id in sample_ids:
        multiqc_path = path(outdata_dir).joinpath(sample_id, multiqc_samtools)
        if multiqc_path.exists():
            log.debug("calculate total mapped reads for: %s", sample_id)
            with open(multiqc_path, 'r') as stream:
                mapped_data = total_mapped(stream)
                qc_samples[sample_id] = mapped_data
        else:
            log.warn("multiqc output missing for %s", sample_id)
            qc_samples[sample_id] = {}

        # duplicates
        log.debug("calculate duplicates for: %s", sample_id)
        duplicates = get_duplicates(outdata_dir, sample_id)
        qc_samples[sample_id]['duplicates'] = duplicates

    log.debug("parse QC metrics YAML: %s", qcmetrics_path)
    with open(qcmetrics_path, 'r') as stream:
        qc_data = yaml.load(stream)
        qc_rootkey = 'sample' if 'sample' in qc_data else qc_data.keys()[0]

    for sample_id, mapped_data in qc_samples.items():
        qc_data[qc_rootkey][sample_id]['MappedReads'] = mapped_data.get('mapped')
        qc_data[qc_rootkey][sample_id]['TotalReads'] = mapped_data.get('total')
        qc_data[qc_rootkey][sample_id]['MappedRate'] = mapped_data.get('percentage')
        qc_data[qc_rootkey][sample_id]['Duplicates'] = mapped_data['duplicates']

    new_qcmetrics = path(qcmetrics_path.replace('.yaml', '.mod.yaml'))
    log.info("create updated qc metrics: %s", new_qcmetrics)
    with new_qcmetrics.open('w') as stream:
        dump = yaml.dump(qc_data, default_flow_style=False, allow_unicode=True)
        stream.write(dump.decode('utf-8'))


def total_mapped(stream):
    """Extract the percentage of mapped reads across all lanes."""
    data = csv.DictReader(stream, delimiter='\t', quoting=csv.QUOTE_NONE)
    total = 0
    mapped = 0
    for row in data:
        total += float(row.get('raw total sequences') or
                       row['raw_total_sequences'])
        mapped += float(row.get('reads mapped') or row['reads_mapped'])
    return {'mapped': mapped, 'total': total, 'percentage': mapped / total}


def get_duplicates(outdata_dir, sample_id):
    """Parse out the duplicate rate."""
    files = path(outdata_dir).glob("{0}/bwa/{0}_lanes_*_sorted_md_metric"
                                   .format(sample_id))
    if len(files) == 1:
        with open(files[0], 'r') as stream:
            content = stream.read()
        dups = float(re.search('Fraction Duplicates: (.*)', content).groups()[0])
    else:
        raise IOError('no picard tools file!')
    return dups
