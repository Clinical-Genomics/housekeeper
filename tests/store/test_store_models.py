# -*- coding: utf-8 -*-
import json

from housekeeper.store import Sample


def test_to_json():
    # GIVEN a basic sample model
    sample_name = 'ADM12'
    new_sample = Sample(lims_id=sample_name)
    # WHEN serializing to JSON
    sample_json = new_sample.to_json()
    # THEN it should return a serialized dict
    data = json.loads(sample_json)
    assert data['lims_id'] == sample_name
