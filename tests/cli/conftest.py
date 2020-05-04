"""Fixtures for CLI tests"""

import pytest
from click.testing import CliRunner


@pytest.fixture(name="cli_runner")
def fixture_cli_runner():
    """Return a cli runner for testing Click"""
    runner = CliRunner()
    return runner


@pytest.fixture(name="base_context")
def fixture_base_context(db_uri, project_dir, store):
    """Return a context with initialized database"""
    _ctx = {
        "database": db_uri,
        "root": project_dir,
        "store": store,
    }
    return _ctx
