"""Fixtures for CLI tests"""

import datetime
from pathlib import Path
from typing import Generator

import pytest
from click.testing import CliRunner

from housekeeper.services.file_service.file_service import FileService
from housekeeper.services.file_report_service.file_report_service import FileReportService
from housekeeper.store.database import (
    create_all_tables,
    drop_all_tables,
    initialize_database,
)
from housekeeper.store.store import Store
from tests.helper_functions import Helpers


@pytest.fixture(scope="function")
def store(project_dir: Path, db_uri: str) -> Generator[Store, None, None]:
    """Override the store fixture to get a controlled db path."""
    initialize_database(db_uri)
    _store = Store(root=str(project_dir))
    create_all_tables()
    yield _store
    drop_all_tables()


@pytest.fixture(scope="function")
def cli_runner():
    """Return a cli runner for testing Click"""
    return CliRunner()


@pytest.fixture
def output_service() -> FileReportService:
    return FileReportService()


@pytest.fixture
def file_service(store: Store) -> FileService:
    return FileService(store)


@pytest.fixture
def base_context(
    db_uri, project_dir, store, file_service: FileService, output_service: FileReportService
) -> dict:
    """Return a context with initialized database"""
    return {
        "database": db_uri,
        "root": project_dir,
        "store": store,
        "file_service": file_service,
        "file_report_service": output_service,
    }


@pytest.fixture
def populated_context(db_uri, project_dir, populated_store, file_service, output_service) -> dict:
    """Return a context with initialized database with some data"""
    return {
        "database": db_uri,
        "root": project_dir,
        "store": populated_store,
        "file_service": file_service,
        "file_report_service": output_service,
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
