"""Fixture for the Store tests"""

import datetime
import datetime as dt
from copy import deepcopy

import pytest

from housekeeper.store import models


@pytest.fixture(scope="function")
def minimal_bundle_obj(case_id, timestamp) -> models.Bundle:
    """Return a bundle object"""
    return models.Bundle(name=case_id, created_at=timestamp)


@pytest.fixture(scope="function")
def bundle_data_json(bundle_data):
    """Fixture for bundle data in json format"""
    json_data = deepcopy(bundle_data)
    json_data["created_at"] = json_data["created_at"].isoformat()
    return json_data


@pytest.fixture(scope="function")
def second_timestamp(timestamp) -> datetime.datetime:
    """Return a time stamp in date time format"""
    return timestamp + datetime.timedelta(days=10)


@pytest.fixture(scope="function")
def old_timestamp() -> datetime.datetime:
    """Return a time stamp that is older than a year"""
    return datetime.datetime(2018, 1, 1)


@pytest.fixture(scope="function")
def second_bundle_data(bundle_data, second_sample_vcf, second_family_vcf, second_timestamp) -> dict:
    """Return a bundle similar to bundle_data with updated file paths"""
    second_bundle = deepcopy(bundle_data)
    second_bundle["created_at"] = second_timestamp
    second_bundle["files"][0]["path"] = str(second_sample_vcf)
    second_bundle["files"][1]["path"] = str(second_family_vcf)
    return second_bundle


@pytest.fixture(scope="function")
def other_case() -> str:
    """Return the case id that differs from base fixture"""
    return "angrybird"


@pytest.fixture(scope="function")
def bundle_data_old(
    bundle_data, second_sample_vcf, second_family_vcf, old_timestamp, other_case
) -> dict:
    """Return info for a older bundle with different files and case id as bundle data"""
    _bundle = deepcopy(bundle_data)
    _bundle["name"] = other_case
    _bundle["created_at"] = old_timestamp
    _bundle["files"][0]["path"] = str(second_sample_vcf)
    _bundle["files"][1]["path"] = str(second_family_vcf)
    return _bundle


@pytest.fixture(scope="function")
def time_stamp_now() -> dt.datetime:
    """Time stamp now"""
    return dt.datetime.now()
