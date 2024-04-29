"""Fixtures for the CLI add tests"""

import json
from pathlib import Path

import pytest


@pytest.fixture
def file_data(second_sample_vcf: Path, case_id: str, sample_tag_names: list[str]) -> dict:
    """Return a dictionary with file information"""
    return {"path": str(second_sample_vcf), "tags": sample_tag_names, "bundle": case_id}


@pytest.fixture
def file_data_json(file_data) -> str:
    """Return a json string with file information"""
    return json.dumps(file_data)
