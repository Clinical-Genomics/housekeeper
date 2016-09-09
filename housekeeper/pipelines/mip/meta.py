# -*- coding: utf-8 -*-
import yaml


def build_meta(name, run, qc_ped):
    """Build metadata information content.

    Args:
        analysis (Analysis): analysis record
        qc_ped (path): path to qc pedigree file

    Returns:
        str: YAML-formatted string of the data
    """
    with open(qc_ped, 'r') as stream:
        qcped_data = yaml.load(stream)
    metadata = analysis_metadata(name, run)
    sample_map = sampleid_map(qcped_data)
    metadata['samples'] = sample_map
    return yaml.dump(metadata)


def analysis_metadata(name, run):
    """Build metadata information about an analysis run/case."""
    data = {
        'name': name,
        'analyzed_at': run.analyzed_at,
        'pipeline': run.pipeline,
        'pipeline_version': run.pipeline_version,
    }
    return data


def sampleid_map(qc_ped):
    """Take out information about internal/external sample names."""
    fam_key = qc_ped.keys()[0]
    samples = {}
    for sample in qc_ped[fam_key].values():
        samples[sample['Individual ID']] = sample['display_name'][0]
    return samples
