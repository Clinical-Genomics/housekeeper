# -*- coding: utf-8 -*-
import yaml

from housekeeper.exc import MalformattedPedigreeError


def write_meta(meta_output, outdata_dir):
    """Write meta files."""
    meta_path = "{}/meta.yaml".format(outdata_dir)
    with open(meta_path, 'w') as out_handle:
        out_handle.write(meta_output)


def build_meta(case_name, family_data, qc_ped, version=None, strict=True):
    """Build metadata information content.

    Args:
        run (AnalysisRun): analysis run record
        qc_ped (path): path to qc pedigree file

    Returns:
        str: YAML-formatted string of the data
    """
    with open(qc_ped, 'r') as stream:
        qcped_data = yaml.load(stream)
    sample_map = sampleid_map(qcped_data, strict=strict)
    metadata = {
        'name': case_name,
        'pipeline': 'mip',
        'pipeline_version': version or family_data['MIPVersion'],
        'analyzed_at': family_data['AnalysisDate'],
        'samples': sample_map,
    }
    return yaml.dump(metadata, default_flow_style=False)


def sampleid_map(qc_ped, strict=True):
    """Take out information about internal/external sample names."""
    fam_key = qc_ped.keys()[0]
    samples = {}
    for sample in qc_ped[fam_key].values():
        sample_id = sample.get('Individual ID', sample.get('SampleID'))
        if sample_id is None:
            raise MalformattedPedigreeError(fam_key)
        sample_names = sample.get('display_name')
        if sample_names is None and not strict:
            sample_names = sample.get('Display_name')
        if isinstance(sample_names, list):
            samples[sample_id] = sample_names[0]
        else:
            message = "{}: 'display_name'".format(fam_key)
            raise MalformattedPedigreeError(message)

    return samples
