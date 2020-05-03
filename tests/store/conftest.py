"""Fixture for the Store tests"""
import datetime
from copy import deepcopy

import pytest

from housekeeper.store import models


@pytest.fixture(scope="function", name="bundle_obj")
def fixture_bundle_obj(case_id, timestamp) -> models.Bundle:
    """Return a bundle object"""
    return models.Bundle(name=case_id, created_at=timestamp)


@pytest.fixture(scope="function", name="old_timestamp")
def fixture_old_timestamp() -> datetime.datetime:
    """Return a time stamp that is older than a year"""
    return datetime.datetime(2018, 1, 1)


@pytest.fixture(scope="function", name="other_case")
def fixture_other_case() -> str:
    """Return the case id that differs from base fixture"""
    return "angrybird"


@pytest.fixture(scope="function", name="bundle_data_old")
def bundle_data_old(
    bundle_data, second_sample_vcf, second_family_vcf, old_timestamp
) -> dict:
    """Return info for a older bundle with different files and case id as bundle data"""
    _bundle = deepcopy(bundle_data)
    _bundle["created"] = old_timestamp
    _bundle["files"][0]["path"] = str(second_sample_vcf)
    _bundle["files"][1]["path"] = str(second_family_vcf)
    return _bundle
