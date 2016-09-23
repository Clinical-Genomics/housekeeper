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
        try:
            keys = reference['key'].split('|')
            source = segments[reference['source']]
            if reference.get('sample'):
                for sample_id, values in source.items():
                    ref_paths = parse_tree(values, keys)
                    for ref_path in ref_paths:
                        ref_path = format_path(reference, ref_path)
                        yield {'reference': reference, 'path': ref_path,
                               'sample': sample_id}
            else:
                ref_paths = parse_tree(source, keys)
                for ref_path in ref_paths:
                    ref_path = format_path(reference, ref_path)
                    yield {'reference': reference, 'path': ref_path}
        except KeyError as error:
            if reference.get('required') is False:
                log.warn(error.message)
                continue
            else:
                raise error


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


def format_path(reference, orig_path):
    """Get a file from analysis output."""
    if 'suffix' in reference:
        new_path = orig_path + reference['suffix']
    elif 'replace' in reference:
        new_path = orig_path.replace(reference['replace']['old_str'],
                                     reference['replace']['new_str'])
    else:
        new_path = orig_path
    return new_path


def parse_tree(tree, keys):
    """Parse a dict using a list of keys."""
    for index, key in enumerate(keys):
        if key.isdigit():
            if isinstance(tree, dict):
                tree = tree.values()[int(key)]
            else:
                tree = tree[int(key)]
        elif key == '*':
            subtrees = tree.values()
            paths = []
            for subtree in subtrees:
                values = parse_tree(subtree, keys[index + 1:])
                for value in values:
                    paths.append(value)
            return paths
        else:
            tree = tree[key]
    return [tree]
