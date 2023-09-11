"""Fixtures for CLI tests"""
import datetime

import pytest
from click.testing import CliRunner
from housekeeper.store import Store
from tests.helper_functions import Helpers


@pytest.fixture(scope="function")
def store(project_dir, db_uri):
    """Override the store fixture to get a controlled db path"""
    _store = Store(uri=db_uri, root=str(project_dir))
    _store.create_all()
    yield _store
    _store.drop_all()


@pytest.fixture(scope="function")
def cli_runner():
    """Return a cli runner for testing Click"""
    return CliRunner()


@pytest.fixture(scope="function")
def base_context(db_uri, project_dir, store) -> dict:
    """Return a context with initialized database"""
    return {
        "database": db_uri,
        "root": project_dir,
        "store": store,
    }


@pytest.fixture(scope="function")
def populated_context(db_uri, project_dir, populated_store) -> dict:
    """Return a context with initialized database with some data"""
    return {
        "database": db_uri,
        "root": project_dir,
        "store": populated_store,
    }


@pytest.fixture(scope="function")
def populated_store_subsequent(
    store: Store, bundle_data_subsequent: dict, helpers: Helpers
) -> Store:
    """Returns a populated store"""
    helpers.add_bundle(store, bundle_data_subsequent)
    return store


@pytest.fixture(scope="function")
def populated_context_subsequent(db_uri, project_dir, populated_store_subsequent):
    """Return a context with initialized database with some data"""
    return {
        "database": db_uri,
        "root": project_dir,
        "store": populated_store_subsequent,
    }


@pytest.fixture(scope="function")
def bundle_data_subsequent(
    case_id: str,
    family_data: dict,
    family2_data: dict,
    family3_data: dict,
    timestamp: datetime.datetime,
) -> dict:
    """Return a bundle."""
    return {
        "name": case_id,
        "created_at": timestamp,
        "files": [
            {
                "path": str(family_data["file"]),
                "archive": False,
                "tags": family_data["tags"],
            },
            {
                "path": str(family2_data["file"]),
                "archive": False,
                "tags": family2_data["tags"],
            },
            {
                "path": str(family3_data["file"]),
                "archive": True,
                "tags": family3_data["tags"],
            },
        ],
    }
