# -*- coding: utf-8 -*-
import logging

from path import path
import yaml

from housekeeper.exc import MissingFileError

log = logging.getLogger(__name__)


def parse_references(references, segments):
    """Combine the functions."""
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
        except (KeyError, MissingFileError) as error:
            if reference.get('required') is False:
                log.warn(error.message)
                continue
            else:
                log.error("source: {}, key: {}".format(reference['source'],
                                                       reference['key']))
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
    elif 'glob' in reference:
        matches = path(orig_path).glob(reference['glob'])
        if len(matches) == 0:
            glob = reference['glob']
            raise MissingFileError("missing: {}, {}".format(orig_path, glob))
        new_path = matches[0]
    else:
        new_path = orig_path
    return new_path


def parse_tree(tree, keys):
    """Parse a dict using a list of keys."""
    for index, key in enumerate(keys):
        if key.isdigit():
            if isinstance(tree, dict):
                tree = list(tree.values())[int(key)]
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
