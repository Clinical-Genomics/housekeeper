"""Fixtures for the CLI add tests"""
import json
from pathlib import Path
from typing import List

import pytest


@pytest.fixture(name="file_data")
def fixture_file_data(second_sample_vcf: Path, case_id: str, sample_tag_names: List[str]) -> dict:
    """Return a dictionary with file information"""
    return {"path": str(second_sample_vcf), "tags": sample_tag_names, "bundle": case_id}


@pytest.fixture(name="file_data_json")
def fixture_file_data_json(file_data) -> str:
    """Return a json string with file information"""
    return json.dumps(file_data)
