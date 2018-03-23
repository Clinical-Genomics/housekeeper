# -*- coding: utf-8 -*-
from copy import deepcopy
import datetime
import pytest

import tempfile


@pytest.fixture(scope='function')
def bundle_data_json(bundle_data):
    json_data = deepcopy(bundle_data)
    json_data['created'] = json_data['created'].isoformat()
    json_data['expires'] = json_data['expires'].isoformat()
    return json_data
