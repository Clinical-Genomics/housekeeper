# -*- coding: utf-8 -*-
import json

from housekeeper.store import Metadata, Sample


def test_to_json():
    # GIVEN a basic sample model
    sample_name = 'ADM12'
    new_sample = Sample(name=sample_name)
    # WHEN serializing to JSON
    sample_json = new_sample.to_json()
    # THEN it should return a serialized dict
    data = json.loads(sample_json)
    assert data['name'] == sample_name


def test_analysis_analyses_root():
    # GIVEN an Metadata model with a root path
    root_path = '/tmp/space'
    meta = Metadata(root=root_path)
    # WHEN accessing the root for analyses
    analyses_root = meta.analyses_root
    # THEN it should append '/analyses'
    assert analyses_root.endswith('/analyses')
