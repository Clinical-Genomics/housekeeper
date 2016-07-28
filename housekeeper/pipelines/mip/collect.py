# -*- coding: utf-8 -*-
from __future__ import division
import csv
import logging

from path import path
import yaml

from housekeeper.pipelines.general.add import asset as general_asset
from housekeeper.pipelines.general.add import analysis as general_analysis

MULTIQC_SAMTOOLS = 'multiqc/multiqc_data/multiqc_samtools.txt'

log = logging.getLogger(__name__)


def analysis(config_path):
    """Prepare info for a MIP analysis."""
    with open(config_path, 'r') as stream:
        config = yaml.load(stream)

    sampleinfo_path = config['sampleInfoFile']
    with open(sampleinfo_path, 'r') as stream:
        sampleinfo = yaml.load(stream)

    fam_key = sampleinfo.keys()[0]
    family = sampleinfo[fam_key][fam_key]

    analyzed_at = family['AnalysisDate']
    version = family['MIPVersion']
    sample_ids = config['sampleIDs']
    customer = family['InstanceTag'][0]
    name = "{}-{}".format(customer, fam_key)
    new_analysis = general_analysis(name, 'mip', version, analyzed_at,
                                    sample_ids)
    new_samples = {sample.name: sample for sample in new_analysis.samples}

    ped = family['PedigreeFile']['Path']
    bcf_raw = family['BCFFile']['Path']
    bcf_clinical = family['BCFFile']['Clinical']['Path']
    bcf_research = family['BCFFile']['Research']['Path']
    qc_metrics = family['Program']['QCCollect']['QCCollectMetricsFile']['Path']
    log_file = family['lastLogFilePath']

    assets = [
        general_asset(ped, 'pedigree'),
        general_asset(bcf_raw, 'vcf-raw', for_archive=True),
        general_asset(bcf_clinical, 'vcf-clinical', for_archive=True),
        general_asset(bcf_research, 'vcf-research', for_archive=True),
        general_asset(log_file, 'log', for_archive=True),
    ]

    for sample_id in sample_ids:
        sample = sampleinfo[fam_key][sample_id]

        coverage_files = sample['Program']['SambambaDepth'].values()
        assert len(coverage_files) == 1
        coverage = coverage_files[0]['Bed']['Path']
        coverage_asset = general_asset(coverage, 'coverage')
        assets.append(coverage_asset)
        new_samples[sample_id].assets.append(coverage_asset)

        complete_bam = sample['MostCompleteBAM']['Path']
        bam_asset = general_asset(complete_bam, 'bam')
        bai_asset = general_asset("{}.bai".format(complete_bam), 'bai')
        assets.append(bam_asset)
        assets.append(bai_asset)
        new_samples[sample_id].assets.append(bam_asset)
        new_samples[sample_id].assets.append(bai_asset)

        for input_file in sample['File'].values():
            cram = input_file['CramFile']
            cram_asset = general_asset(cram, 'cram', for_archive=True)
            assets.append(cram_asset)
            new_samples[sample_id].assets.append(cram_asset)

    # multiqc outputs
    qc_samples = {}
    for sample_id in sample_ids:
        out_root = path(config['outDataDir'])
        multiqc_path = out_root.joinpath(sample_id, MULTIQC_SAMTOOLS)
        mapped_reads = total_mapped(multiqc_path)
        qc_samples[sample_id] = mapped_reads

    with open(qc_metrics, 'r') as stream:
        qc_data = yaml.load(stream)
        qc_rootkey = qc_data.keys()[0]

    for sample_id, mapped_reads in qc_samples.items():
        qc_data[qc_rootkey][sample_id]['MappedReads'] = mapped_reads

    log.info('create updated qc metrics')
    new_qcmetrics = path(qc_metrics.replace('.yaml', '.mod.yaml'))
    with new_qcmetrics.open('w') as stream:
        dump = yaml.dump(qc_data, default_flow_style=False, allow_unicode=True)
        stream.write(dump.decode('utf-8'))
    assets.append(general_asset(new_qcmetrics, 'qc', for_archive=True))

    for asset in assets:
        new_analysis.assets.append(asset)
    return new_analysis


def total_mapped(multiqc_path):
    """Extract the percentage of mapped reads across all lanes."""
    with open(multiqc_path, 'r') as stream:
        data = csv.DictReader(stream, delimiter='\t', quoting=csv.QUOTE_NONE)
        total = 0
        mapped = 0
        for row in data:
            total += float(row['raw total sequences'])
            mapped += float(row['reads mapped'])
    return mapped / total
