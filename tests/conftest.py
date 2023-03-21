"""Base fixtures"""
import copy
import datetime
import json
import shutil
from copy import deepcopy
from pathlib import Path
from typing import List

import pytest
import yaml

from housekeeper.date import get_date
from housekeeper.store import Store, models

from .helper_functions import Helpers


# basic fixtures

@pytest.fixture(scope="function", name="helpers")
def fixture_helpers() -> Helpers:
    """Return a test helper object."""
    return Helpers()


@pytest.fixture(scope="function", name="vcf_tag_name")
def fixture_vcf_tag_name() -> str:
    """Return a tag named 'vcf'."""
    return "vcf"


@pytest.fixture(scope="function", name="family_tag_name")
def fixture_family_tag_name() -> str:
    """Return a tag named 'family'."""
    return "family"


@pytest.fixture(scope="function", name="sample_tag_name")
def fixture_sample_tag_name() -> str:
    """Return a tag named 'sample'."""
    return "sample"


@pytest.fixture(scope="function", name="non_existent_tag_name")
def fixture_non_existent_tag_name() -> str:
    """Return a non-existent tag name."""
    return "not_a_tag_name"


@pytest.fixture(scope="function", name="family_tag_names")
def fixture_family_tag_names(vcf_tag_name: str, family_tag_name: str) -> List[str]:
    """Return a list of the family tag names."""
    return [vcf_tag_name, family_tag_name]


@pytest.fixture(scope="function", name="sample_tag_names")
def fixture_sample_tag_names(vcf_tag_name: str, sample_tag_name: str) -> List[str]:
    """Return a list of the sample tag names."""
    return [vcf_tag_name, sample_tag_name]


@pytest.fixture(scope="function", name="case_id")
def fixture_case_id() -> str:
    """Return name of a case."""
    return "handsomepig"


@pytest.fixture(scope="function", name="other_case_id")
def fixture_other_case_id() -> str:
    """Return name of a another case."""
    return "maturecogar"


@pytest.fixture(scope="function", name="sample_data")
def fixture_sample_data(sample_tag_names: List[str], sample_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": sample_tag_names, "file": sample_vcf}


@pytest.fixture(scope="function", name="sample2_data")
def fixture_sample2_data(sample_tag_names: List[str], second_sample_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": sample_tag_names, "file": second_sample_vcf}


@pytest.fixture(scope="function", name="family_data")
def fixture_family_data(family_tag_names: List[str], family_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": family_tag_names, "file": family_vcf}


@pytest.fixture(scope="function", name="family2_data")
def fixture_family2_data(family_tag_names: List[str], second_family_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": family_tag_names, "file": second_family_vcf}


@pytest.fixture(scope="function", name="family3_data")
def fixture_family3_data(family_tag_names: List[str], third_family_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": family_tag_names, "file": third_family_vcf}


@pytest.fixture(scope="function", name="timestamp_string")
def fixture_timestamp_string() -> str:
    """Return a time stamp in str format."""
    return "2020-05-01"


@pytest.fixture(scope="function", name="timestamp")
def fixture_timestamp(timestamp_string: str) -> datetime.datetime:
    """Return a time stamp in date time format."""
    return get_date(timestamp_string)


@pytest.fixture(scope="function", name="later_timestamp")
def fixture_later_timestamp() -> datetime.datetime:
    """Return a time stamp in date time format to a later date."""
    return datetime.datetime(2020, 5, 25)


@pytest.fixture(scope="function", name="bundle_data")
def fixture_bundle_data(
    case_id: str, sample_data: dict, family_data: dict, timestamp: datetime.datetime, helpers: Helpers
) -> dict:
    """Return a bundle."""
    data = helpers.create_bundle_data(case_id=case_id, files=[family_data, sample_data], created_at=timestamp)
    return data


@pytest.fixture(scope="function", name="empty_version_data")
def fixture_empty_version_data(later_timestamp: datetime.datetime, case_id: str) -> dict:
    """Return a dummy bundle."""
    data = {"bundle_name": case_id, "created_at": later_timestamp, "files": []}
    return data


@pytest.fixture(scope="function", name="version_data")
def fixture_version_data(empty_version_data: dict, family2_data: dict, sample2_data: dict) -> dict:
    """Return a dummy bundle."""
    data = copy.deepcopy(empty_version_data)
    data["files"] = [
        {
            "path": str(sample2_data["file"]),
            "archive": False,
            "tags": sample2_data["tags"],
        },
        {
            "path": str(family2_data["file"]),
            "archive": True,
            "tags": family2_data["tags"],
        },
    ]
    return data


@pytest.fixture(scope="function", name="bundle_data_json")
def fixture_bundle_data_json(bundle_data: dict) -> str:
    """Return a dummy bundle."""
    json_data = copy.deepcopy(bundle_data)
    json_data["created_at"] = str(json_data.pop("created_at"))
    return json.dumps(json_data)


@pytest.fixture(scope="function", name="empty_version_data_json")
def fixture_empty_version_data_json(empty_version_data: dict) -> str:
    """Return a dummy bundle."""
    json_data = copy.deepcopy(empty_version_data)
    json_data["created_at"] = str(json_data.pop("created_at"))
    return json.dumps(json_data)


@pytest.fixture(scope="function", name="version_data_json")
def fixture_version_data_json(version_data: dict) -> str:
    """Return a dummy bundle."""
    json_data = copy.deepcopy(version_data)
    json_data["created_at"] = str(json_data.pop("created_at"))
    return json.dumps(json_data)


@pytest.fixture(scope="function", name="other_bundle")
def fixture_other_bundle(
        bundle_data: dict,
        other_case_id: str,
        later_timestamp: datetime.datetime,
        second_sample_vcf: Path,
        second_family_vcf: Path,
) -> dict:
    """Return a dummy bundle."""
    data = deepcopy(bundle_data)
    data["name"] = other_case_id
    data["created_at"] = later_timestamp
    data["files"][0]["path"] = str(second_sample_vcf)
    data["files"][1]["path"] = str(second_family_vcf)
    return data


@pytest.fixture(scope="function", name="db_name")
def fixture_db_name() -> str:
    """Return the name of a database."""
    return "hk_test.db"


@pytest.fixture(scope="function", name="db_path")
def fixture_db_path(db_dir: Path, db_name: str) -> Path:
    """Return the path to a database."""
    return db_dir / db_name


@pytest.fixture(scope="function", name="db_uri")
def fixture_db_uri(db_path: Path) -> str:
    """Return the uri to an in memory database."""
    return "sqlite:///" + str(db_path)


@pytest.fixture(scope="function", name="db_uri_memory")
def fixture_db_uri_memory() -> str:
    """Return the uri to an in memory database."""
    return "sqlite:///:memory:"


@pytest.fixture(scope="function", name="configs")
def fixture_configs(project_dir: Path, db_uri: str) -> dict:
    """Return a dict with housekeeper configs."""
    _configs = {"root": str(project_dir), "database": db_uri}
    return _configs


# object fixtures


@pytest.fixture(scope="function", name="vcf_tag_obj")
def fixture_vcf_tag_obj(vcf_tag_name: str, timestamp: datetime.datetime) -> str:
    """Return a tag object."""
    return models.Tag(name=vcf_tag_name, created_at=timestamp)


@pytest.fixture(scope="function", name="bundle_obj")
def fixture_bundle_obj(bundle_data: dict, store: Store) -> models.Bundle:
    """Return a bundle object."""
    return store.add_bundle(bundle_data)[0]


@pytest.fixture(scope="function", name="version_obj")
def fixture_version_obj(bundle_data: dict, store: Store) -> models.Version:
    """Return a version object."""
    return store.add_bundle(bundle_data)[1]


# dir fixtures


@pytest.fixture(scope="function", name="fixtures_dir")
def fixture_fixtures_dir() -> Path:
    """Return the path to the fixtures directory."""
    return Path("tests/fixtures/")


@pytest.fixture(scope="function", name="vcf_dir")
def fixture_vcf_dir(fixtures_dir: Path) -> Path:
    """Return the path to the vcf fixtures directory."""
    return fixtures_dir / "vcfs"


@pytest.fixture(scope="function", name="project_dir")
def fixture_project_dir(tmpdir_factory) -> Path:
    """Path to a temporary working directory."""
    my_tmpdir = Path(tmpdir_factory.mktemp("workdir"))
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


@pytest.fixture(scope="function", name="config_dir")
def fixture_config_dir(tmpdir_factory) -> Path:
    """Path to a temporary directory for config files."""
    my_tmpdir = Path(tmpdir_factory.mktemp("confdir"))
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


@pytest.fixture(scope="function", name="db_dir")
def fixture_db_dir(tmpdir_factory) -> Path:
    """Path to a temporary directory for databases."""
    my_tmpdir = Path(tmpdir_factory.mktemp("db_dir"))
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


# File fixtures


@pytest.fixture(scope="function", name="config_file")
def fixture_config_file(config_dir: Path, configs: dict) -> Path:
    """Create a config file and return the path to it."""
    conf_path = config_dir / "config.json"
    with open(conf_path, "w") as out_file:
        yaml.dump(configs, out_file)
    return conf_path


@pytest.fixture(scope="function", name="sample_vcf")
def fixture_sample_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return vcf_dir / "example.vcf"


@pytest.fixture(scope="function", name="family_vcf")
def fixture_family_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return vcf_dir / "family.vcf"


@pytest.fixture(scope="function", name="second_sample_vcf")
def fixture_second_sample_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return vcf_dir / "example.2.vcf"


@pytest.fixture(scope="function", name="second_family_vcf")
def fixture_second_family_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return vcf_dir / "family.2.vcf"


@pytest.fixture(scope="function", name="third_family_vcf")
def fixture_third_family_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return vcf_dir / "family.3.vcf"


@pytest.fixture(scope="function", name="checksum_file")
def fixture_checksum_file(fixtures_dir: Path) -> Path:
    """Return the path to file to test checksum."""
    return fixtures_dir / "26a90105b99c05381328317f913e9509e373b64f.txt"


@pytest.fixture(scope="function", name="checksum")
def fixture_checksum(checksum_file: Path) -> Path:
    """Return the checksum for checksum test file."""
    return checksum_file.name.rstrip(".txt")


@pytest.fixture(scope="function", name="helpers")
def fixture_helpers() -> Helpers:
    """Return a test helper object."""
    return Helpers()

# Store fixtures


@pytest.fixture(scope="function", name="store")
def fixture_store(project_dir: Path) -> Store:
    """Return a store setup with all tables."""
    _store = Store(uri="sqlite:///", root=str(project_dir))
    _store.create_all()
    yield _store
    _store.drop_all()


@pytest.fixture(scope="function", name="populated_store")
def fixture_populated_store(store: Store, bundle_data: dict, helpers: Helpers) -> Store:
    """Returns a populated store."""
    helpers.add_bundle(store, bundle_data)
    return store
