"""Fixture for the Store tests"""

import pytest

from housekeeper.store import models


@pytest.fixture(scope="function", name="bundle_obj")
def fixture_bundle_obj(case_id, timestamp) -> models.Bundle:
    """Return a bundle object"""
    return models.Bundle(name=case_id, created_at=timestamp)
