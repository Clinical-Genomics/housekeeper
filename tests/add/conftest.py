"""Fixtures for housekeeper add"""
import datetime
from copy import deepcopy
from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def bundle_data_json(bundle_data):
    """Fixture for bundle data in json format"""
    json_data = deepcopy(bundle_data)
    json_data["created"] = json_data["created"].isoformat()
    json_data["expires"] = json_data["expires"].isoformat()
    return json_data


@pytest.fixture(scope="function", name="second_sample_vcf")
def fixture_second_sample_vcf(fixtures_dir) -> Path:
    """Return the path to a vcf file"""
    return fixtures_dir / "example.2.vcf"


@pytest.fixture(scope="function", name="second_family_vcf")
def fixture_second_family_vcf(fixtures_dir) -> Path:
    """Return the path to a vcf file"""
    return fixtures_dir / "family.2.vcf"


@pytest.fixture(scope="function", name="second_timestamp")
def fixture_second_timestamp(timestamp) -> datetime.datetime:
    """Return a time stamp in date time format"""
    return timestamp + datetime.timedelta(days=10)


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
