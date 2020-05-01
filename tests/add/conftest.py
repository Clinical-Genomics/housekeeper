"""Fixtures for housekeeper add"""
from copy import deepcopy
import pytest


@pytest.fixture(scope='function')
def bundle_data_json(bundle_data):
    """Fixture for bundle data in json format"""
    json_data = deepcopy(bundle_data)
    json_data['created'] = json_data['created'].isoformat()
    json_data['expires'] = json_data['expires'].isoformat()
    return json_data
