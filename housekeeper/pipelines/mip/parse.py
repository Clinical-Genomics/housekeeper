# -*- coding: utf-8 -*-
import logging

import yaml

log = logging.getLogger(__name__)


def parse_references(references, params, segments):
    """Combine the functions."""
    with open(params['config'], 'r') as in_handle:
        config_data = yaml.load(in_handle)
    segments = prepare_inputs(config_data)
    for reference in references:
        if reference['source'] == 'param':
            path = params[reference['key']]
            yield {'reference': reference, 'path': path}
        else:
            source = segments[reference['source']]
            if reference.get('sample'):
                for sample_id, values in source.items():
                    path = get_path(reference, values)
                    yield {'reference': reference, 'path': path,
                           'sample': sample_id}
            else:
                path = get_path(reference, source)
                yield {'reference': reference, 'path': path}


def prepare_inputs(config_data):
    """Parse input and pick out segments."""
    fam_key = config_data['familyID']
    sampleinfo_path = config_data['sampleInfoFile']
    log.debug("parse sampleinfo YAML: %s", sampleinfo_path)
    with open(sampleinfo_path, 'r') as in_handle:
        data = yaml.load(in_handle)
    family = data[fam_key][fam_key]
    samples = {key: subdata for key, subdata in data[fam_key].items()
               if key != fam_key}
    return {'family': family, 'samples': samples, 'config': config_data}


def get_path(reference, source):
    """Get a file from analysis output."""
    keys = reference['key'].split('|')
    for key in keys:
        if key.isdigit():
            if isinstance(source, dict):
                source = source.values()[int(key)]
            else:
                source = source[int(key)]
        else:
            source = source[key]

    if 'suffix' in reference:
        source = source + reference['suffix']
    elif 'replace' in reference:
        source = source.replace(reference['replace']['old_str'],
                                reference['replace']['new_str'])

    return source
