"""Fixture for the Store tests"""

import datetime
import datetime as dt
from copy import deepcopy
from pathlib import Path

import pytest

from housekeeper.store import models
from housekeeper.store.models import Bundle, File, Version
from housekeeper.store.store import Store


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


@pytest.fixture
def store_for_testing_getting_archived_files(store: Store) -> Store:
    """Returns a store containing a bundle with four spring files, one not archived,
    one archived, one being retrieved and one which has been retrieved."""
    tag = store.new_tag(name="spring")
    store.session.add(tag)
    store.session.commit()

    bundle: Bundle = store.new_bundle(name="sample_id", created_at=datetime.datetime.now())
    version: Version = store.new_version(created_at=datetime.datetime.now())
    bundle.versions.append(version)
    not_archived_file: File = store.add_file(
        bundle=bundle, file_path=Path("not", "archived", "file.txt"), tags=["spring"]
    )
    archived_file: File = store.add_file(
        bundle=bundle, file_path=Path("archived", "file.txt"), tags=["spring"]
    )
    archived_file_ongoing_retrieval = store.add_file(
        bundle=bundle,
        file_path=Path("retrieval", "ongoing", "archived", "file.txt"),
        tags=["spring"],
    )
    retrieved_file = store.add_file(
        bundle=bundle, file_path=Path("retrieved", "file.txt"), tags=["spring"]
    )
    store.session.add(bundle)
    store.session.add(not_archived_file)
    store.session.add(archived_file)
    store.session.add(archived_file_ongoing_retrieval)
    store.session.add(retrieved_file)
    store.session.add(version)
    store.session.commit()
    archive_retrieval_not_ongoing = store.create_archive(
        file_id=archived_file.id, archiving_task_id=1
    )
    archive_retrieval_ongoing = store.create_archive(
        file_id=archived_file_ongoing_retrieval.id, archiving_task_id=2
    )
    archive_retrieved = store.create_archive(file_id=retrieved_file.id, archiving_task_id=3)
    archive_retrieval_ongoing.archived_at = datetime.datetime.now()
    archive_retrieval_ongoing.retrieval_task_id = 1
    archive_retrieved.archived_at = datetime.datetime.now()
    archive_retrieved.retrieval_task_id = 2
    archive_retrieved.retrieved_at = datetime.datetime.now()
    store.session.add(archive_retrieval_ongoing)
    store.session.add(archive_retrieval_not_ongoing)
    store.session.add(archive_retrieved)
    store.session.commit()
    return store
