# -*- coding: utf-8 -*-
import yaml

from housekeeper.exc import MalformattedPedigreeError


def build_meta(name, run, qc_ped):
    """Build metadata information content.

    Args:
        run (AnalysisRun): analysis run record
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
        sample_id = sample.get('Individual ID', sample.get('SampleID'))
        if sample_id is None:
            raise MalformattedPedigreeError(fam_key)
        samples[sample_id] = sample['display_name'][0]
    return samples
