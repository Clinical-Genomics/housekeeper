# -*- coding: utf-8 -*-
from copy import deepcopy
import datetime
import pytest


@pytest.fixture(scope='function')
def bundle_data():
    data = {
        'name': 'sillyfish',
        'created': datetime.datetime.now(),
        'expires': datetime.datetime.now(),
        'files': [{
            'path': 'tests/fixtures/example.vcf',
            'archive': False,
            'tags': ['vcf', 'sample']
        }, {
            'path': 'tests/fixtures/family.vcf',
            'archive': True,
            'tags': ['vcf', 'family']
        }]
    }
    return data


@pytest.fixture(scope='function')
def bundle_data_json(bundle_data):
    json_data = deepcopy(bundle_data)
    json_data['created'] = str(json_data['created'])
    json_data['expires'] = str(json_data['expires'])
    return json_data
