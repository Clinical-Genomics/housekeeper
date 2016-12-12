# -*- coding: utf-8 -*-
import yaml


def build_meta(case_name, segments):
    """Build metadata information content.

    Args:
        run (AnalysisRun): analysis run record
        qc_ped (path): path to qc pedigree file

    Returns:
        str: YAML-formatted string of the data
    """
    sample_map = {sample['sample_id']: sample['sample_name']
                  for sample in segments['pedigree']['samples']}
    metadata = {
        'name': case_name,
        'pipeline': 'mip',
        'pipeline_version': segments['family']['mip_version'],
        'analyzed_at': segments['family']['analysis_date'],
        'samples': sample_map,
    }
    return yaml.safe_dump(metadata, default_flow_style=False)
