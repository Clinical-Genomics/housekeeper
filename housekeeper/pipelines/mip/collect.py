# -*- coding: utf-8 -*-
from __future__ import division
import csv
import logging
import re
import tempfile

from path import path
import yaml

from housekeeper.exc import MissingFileError
from housekeeper.pipelines.general.add import asset as general_asset
from housekeeper.pipelines.general.add import analysis as general_analysis
from .meta import build_meta

MULTIQC_SAMTOOLS = 'multiqc/multiqc_data/multiqc_samtools.txt'

log = logging.getLogger(__name__)


def analysis(config_path, analysis_id=None):
    """Prepare info for a MIP analysis."""
    log.debug("parse config YAML: %s", config_path)
    with open(config_path, 'r') as stream:
        config = yaml.load(stream)

    sampleinfo_path = config['sampleInfoFile']
    log.debug("parse sampleinfo YAML: %s", sampleinfo_path)
    with open(sampleinfo_path, 'r') as stream:
        sampleinfo = yaml.load(stream)

    fam_key = sampleinfo.keys()[0]
    family = sampleinfo[fam_key][fam_key]

    analyzed_at = family['AnalysisDate']
    version = family['MIPVersion']
    sample_ids = config['sampleIDs']
    customer = family['InstanceTag'][0]
    name = "{}-{}".format(customer, fam_key)
    log.debug("build new analysis record: %s", name)
    new_analysis = general_analysis(name, 'mip', version, analyzed_at,
                                    sample_ids)
    new_samples = {sample.name: sample for sample in new_analysis.samples}

    ped = family['PedigreeFile']['Path']
    qcped = family['PedigreeFileAnalysis']['Path']
    bcf_raw = family['BCFFile']['Path']
    bcf_raw_index = "{}.csi".format(bcf_raw)
    bcf_clinical = family['BCFFile']['Clinical']['Path']
    bcf_research = family['BCFFile']['Research']['Path']
    vcf_clinical = family['VCFFile']['Clinical']['Path']
    vcf_research = family['VCFFile']['Research']['Path']
    svbcf_raw = family['SVBCFFile']['Path']
    svbcf_clinical = family['SVBCFFile']['Clinical']['Path']
    svbcf_research = family['SVBCFFile']['Research']['Path']
    svvcf_clinical = family['SVVCFFile']['Clinical']['Path']
    svvcf_research = family['SVVCFFile']['Research']['Path']
    qc_metrics = family['Program']['QCCollect']['QCCollectMetricsFile']['Path']
    log_file = family['lastLogFilePath']

    meta_output = build_meta(new_analysis, qcped)

    tmp_dir = tempfile.mkdtemp()
    meta_path = "{}/meta.yaml".format(tmp_dir)
    with open(meta_path, 'w') as out_handle:
        out_handle.write(meta_output)

    assets = [
        general_asset(ped, 'pedigree'),
        general_asset(qcped, 'qcpedigree'),
        general_asset(sampleinfo_path, 'sampleinfo', for_archive=True),
        general_asset(config_path, 'config', for_archive=True),
        general_asset(bcf_raw, 'bcf-raw', for_archive=True),
        general_asset(bcf_raw_index, 'bcf-raw-index'),
        general_asset(bcf_clinical, 'bcf-clinical', for_archive=True),
        general_asset(bcf_research, 'bcf-research', for_archive=True),
        general_asset(vcf_clinical, 'vcf-clinical'),
        general_asset(vcf_research, 'vcf-research'),
        general_asset(svbcf_raw, 'bcf-raw-sv', for_archive=True),
        general_asset(svbcf_clinical, 'bcf-clinical-sv', for_archive=True),
        general_asset(svbcf_research, 'bcf-research-sv', for_archive=True),
        general_asset(svvcf_clinical, 'vcf-clinical-sv'),
        general_asset(svvcf_research, 'vcf-research-sv'),
        general_asset(log_file, 'log', for_archive=True),
        general_asset(meta_path, 'meta', for_archive=True),
    ]

    for sample_id in sample_ids:
        log.debug("parse assets for sample: %s", sample_id)
        sample = sampleinfo[fam_key][sample_id]

        coverage_files = sample['Program']['SambambaDepth'].values()
        assert len(coverage_files) == 1
        coverage = coverage_files[0]['Bed']['Path']
        coverage_asset = general_asset(coverage, 'coverage')
        assets.append(coverage_asset)
        new_samples[sample_id].assets.append(coverage_asset)

        complete_bam = sample['MostCompleteBAM']['Path']
        bam_asset = general_asset(complete_bam, 'bam')
        bai_paths = ["{}.bai".format(complete_bam),
                     complete_bam.replace('.bam', '.bai')]
        existing_bai = [bai_path for bai_path in bai_paths
                        if path(bai_path).exists()]
        if len(existing_bai) == 0:
            raise MissingFileError(bai_paths)
        else:
            bai_path = existing_bai[0]

        bai_asset = general_asset(bai_path, 'bai')
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
        duplicates = get_duplicates(out_root, sample_id)
        qc_samples[sample_id]['duplicates'] = duplicates

    log.debug("parse QC metrics YAML: %s", qc_metrics)
    with open(qc_metrics, 'r') as stream:
        qc_data = yaml.load(stream)
        qc_rootkey = qc_data.keys()[0]

    for sample_id, mapped_data in qc_samples.items():
        qc_data[qc_rootkey][sample_id]['MappedReads'] = mapped_data.get('mapped')
        qc_data[qc_rootkey][sample_id]['TotalReads'] = mapped_data.get('total')
        qc_data[qc_rootkey][sample_id]['MappedRate'] = mapped_data.get('percentage')
        qc_data[qc_rootkey][sample_id]['Duplicates'] = mapped_data['duplicates']

    new_qcmetrics = path(qc_metrics.replace('.yaml', '.mod.yaml'))
    log.info("create updated qc metrics: %s", new_qcmetrics)
    with new_qcmetrics.open('w') as stream:
        dump = yaml.dump(qc_data, default_flow_style=False, allow_unicode=True)
        stream.write(dump.decode('utf-8'))
    assets.append(general_asset(new_qcmetrics, 'qc', for_archive=True))

    log.debug('assciate assets with analysis')
    for asset in assets:
        new_analysis.assets.append(asset)
    return new_analysis


def total_mapped(stream):
    """Extract the percentage of mapped reads across all lanes."""
    data = csv.DictReader(stream, delimiter='\t', quoting=csv.QUOTE_NONE)
    total = 0
    mapped = 0
    for row in data:
        total += float(row['raw total sequences'])
        mapped += float(row['reads mapped'])
    return {'mapped': mapped, 'total': total, 'percentage': mapped / total}


def get_duplicates(out_root, sample_id):
    """Parse out the duplicate rate."""
    files = out_root.glob("{0}/bwa/{0}_lanes_*_sorted_md_metric"
                          .format(sample_id))
    if len(files) == 1:
        with open(files[0], 'r') as stream:
            content = stream.read()
        dups = float(re.search('Fraction Duplicates: (.*)', content).groups()[0])
    else:
        raise Exception('no picard tools file!')
    return dups
