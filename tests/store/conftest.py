"""Fixture for the Store tests"""
import datetime
from copy import deepcopy

import pytest

from housekeeper.store import models


@pytest.fixture(scope="function", name="minimal_bundle_obj")
def fixture_minimal_bundle_obj(case_id, timestamp) -> models.Bundle:
    """Return a bundle object"""
    return models.Bundle(name=case_id, created_at=timestamp)


@pytest.fixture(scope="function")
def bundle_data_json(bundle_data):
    """Fixture for bundle data in json format"""
    json_data = deepcopy(bundle_data)
    json_data["created"] = json_data["created"].isoformat()
    json_data["expires"] = json_data["expires"].isoformat()
    return json_data


@pytest.fixture(scope="function", name="second_timestamp")
def fixture_second_timestamp(timestamp) -> datetime.datetime:
    """Return a time stamp in date time format"""
    return timestamp + datetime.timedelta(days=10)


@pytest.fixture(scope="function", name="old_timestamp")
def fixture_old_timestamp() -> datetime.datetime:
    """Return a time stamp that is older than a year"""
    return datetime.datetime(2018, 1, 1)


@pytest.fixture(scope="function", name="second_bundle_data")
def fixture_second_bundle_data(
    bundle_data, second_sample_vcf, second_family_vcf, second_timestamp
) -> dict:
    """Return a bundle similar to bundle_data with updated file paths"""
    second_bundle = deepcopy(bundle_data)
    second_bundle["created"] = second_timestamp
    second_bundle["files"][0]["path"] = str(second_sample_vcf)
    second_bundle["files"][1]["path"] = str(second_family_vcf)
    return second_bundle


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
