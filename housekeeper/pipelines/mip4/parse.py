# -*- coding: utf-8 -*-
import logging

import yaml

log = logging.getLogger(__name__)


def prepare_inputs(config_data):
    """Parse input and pick out segments."""
    sampleinfo_path = config_data['qccollect_sampleinfo_file']
    log.debug("parse sampleinfo YAML: %s", sampleinfo_path)
    with open(config_data['pedigree_file'], 'r') as in_handle:
        ped_data = yaml.load(in_handle)
    with open(sampleinfo_path, 'r') as in_handle:
        sampleinfo_data = yaml.load(in_handle)
    family = sampleinfo_data
    samples = {sample_id: sample_data for sample_id, sample_data in
               sampleinfo_data['sample'].items()}
    return {'family': family, 'samples': samples, 'config': config_data,
            'pedigree': ped_data}
