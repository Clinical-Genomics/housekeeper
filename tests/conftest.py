"""Base fixtures"""

import copy
import datetime
import json
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Generator

import pytest
import yaml

from housekeeper.date import get_date
from housekeeper.store.database import (
    create_all_tables,
    drop_all_tables,
    initialize_database,
)
from housekeeper.store.models import Archive, Bundle, Tag, Version
from housekeeper.store.store import Store
from tests.helper_functions import Helpers

# basic fixtures


@pytest.fixture(scope="function")
def helpers() -> Helpers:
    """Return a test helper object."""
    return Helpers()


@pytest.fixture(scope="function")
def vcf_tag_name() -> str:
    """Return a tag named 'vcf'."""
    return "vcf"


@pytest.fixture(scope="function")
def family_tag_name() -> str:
    """Return a tag named 'family'."""
    return "family"


@pytest.fixture(scope="function")
def sample_tag_name() -> str:
    """Return a tag named 'sample'."""
    return "sample"


@pytest.fixture(scope="function")
def non_existent_tag_name() -> str:
    """Return a non-existent tag name."""
    return "not_a_tag_name"


@pytest.fixture(scope="function")
def family_tag_names(vcf_tag_name: str, family_tag_name: str) -> list[str]:
    """Return a list of the family tag names."""
    return [vcf_tag_name, family_tag_name]


@pytest.fixture(scope="function")
def sample_tag_names(vcf_tag_name: str, sample_tag_name: str) -> list[str]:
    """Return a list of the sample tag names."""
    return [vcf_tag_name, sample_tag_name]


@pytest.fixture(scope="session")
def spring_tag() -> str:
    """Return the tag marking SPRING files."""
    return "spring"


@pytest.fixture(scope="session")
def sample_id() -> str:
    """Return name of a sample."""
    return "ACC123456A1"


@pytest.fixture(scope="function")
def archiving_task_id() -> int:
    """Return an id of an archiving task."""
    return 1234


@pytest.fixture(scope="session")
def new_archiving_task_id() -> int:
    """Return a new id of an archiving task."""
    return 1235


@pytest.fixture(scope="function")
def retrieval_task_id() -> int:
    """Return an id of a retrieval task."""
    return 4321


@pytest.fixture(scope="function")
def case_id() -> str:
    """Return name of a case."""
    return "handsomepig"


@pytest.fixture(scope="function")
def other_case_id() -> str:
    """Return name of a another case."""
    return "maturecogar"


@pytest.fixture(scope="function")
def sample_data(sample_tag_names: list[str], sample_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": sample_tag_names, "file": sample_vcf}


@pytest.fixture(scope="function")
def sample2_data(sample_tag_names: list[str], second_sample_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": sample_tag_names, "file": second_sample_vcf}


@pytest.fixture(scope="function")
def spring_file_1_with_tags(sample_id: str, spring_tag: str, spring_file_1: Path) -> dict:
    """Return spring file and tags for a sample."""
    return {"tags": [sample_id, spring_tag], "file": spring_file_1}


@pytest.fixture(scope="function")
def spring_file_2_with_tags(sample_id: str, spring_tag: str, spring_file_2: Path) -> dict:
    """Return a second SPRING file and tags for a sample."""
    return {"tags": [sample_id, spring_tag], "file": spring_file_2}


@pytest.fixture(scope="session")
def spring_file_3_with_tags(sample_id: str, spring_tag: str, spring_file_3: Path) -> dict:
    """Return a third SPRING file and tags for a sample."""
    return {"tags": [sample_id, spring_tag], "file": spring_file_3}


@pytest.fixture(scope="function")
def family_data(family_tag_names: list[str], family_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": family_tag_names, "file": family_vcf}


@pytest.fixture(scope="function")
def family2_data(family_tag_names: list[str], second_family_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": family_tag_names, "file": second_family_vcf}


@pytest.fixture(scope="function")
def family3_data(family_tag_names: list[str], third_family_vcf: Path) -> dict:
    """Return file and tags for sample."""
    return {"tags": family_tag_names, "file": third_family_vcf}


@pytest.fixture(scope="function")
def timestamp_string() -> str:
    """Return a time stamp in str format."""
    return "2020-05-01"


@pytest.fixture(scope="function")
def timestamp(timestamp_string: str) -> datetime.datetime:
    """Return a time stamp in date time format."""
    return get_date(timestamp_string)


@pytest.fixture(scope="function")
def later_timestamp() -> datetime.datetime:
    """Return a time stamp in date time format to a later date."""
    return datetime.datetime(2020, 5, 25)


@pytest.fixture(scope="function")
def bundle_data(
    case_id: str,
    sample_data: dict,
    family_data: dict,
    timestamp: datetime.datetime,
    helpers: Helpers,
) -> dict:
    """Return a bundle."""
    data = helpers.create_bundle_data(
        case_id=case_id, files=[family_data, sample_data], created_at=timestamp
    )
    return data


@pytest.fixture(scope="function")
def sample_bundle_data(
    sample_id: str,
    sample_data: dict,
    spring_file_1_with_tags: dict,
    spring_file_2_with_tags: dict,
    spring_file_3_with_tags: dict,
    timestamp: datetime.datetime,
    helpers: Helpers,
) -> dict:
    """Return a bundle containing mock sequencing files."""
    return helpers.create_bundle_data(
        case_id=sample_id,
        files=[spring_file_1_with_tags, spring_file_2_with_tags, spring_file_3_with_tags],
        created_at=timestamp,
    )


@pytest.fixture(scope="function")
def empty_version_data(later_timestamp: datetime.datetime, case_id: str) -> dict:
    """Return a dummy bundle."""
    data = {"bundle_name": case_id, "created_at": later_timestamp, "files": []}
    return data


@pytest.fixture(scope="function")
def version_data(empty_version_data: dict, family2_data: dict, sample2_data: dict) -> dict:
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


@pytest.fixture(scope="function")
def bundle_data_json(bundle_data: dict) -> str:
    """Return a dummy bundle."""
    json_data = copy.deepcopy(bundle_data)
    json_data["created_at"] = str(json_data.pop("created_at"))
    return json.dumps(json_data)


@pytest.fixture(scope="function")
def empty_version_data_json(empty_version_data: dict) -> str:
    """Return a dummy bundle."""
    json_data = copy.deepcopy(empty_version_data)
    json_data["created_at"] = str(json_data.pop("created_at"))
    return json.dumps(json_data)


@pytest.fixture(scope="function")
def version_data_json(version_data: dict) -> str:
    """Return a dummy bundle."""
    json_data = copy.deepcopy(version_data)
    json_data["created_at"] = str(json_data.pop("created_at"))
    return json.dumps(json_data)


@pytest.fixture(scope="function")
def other_bundle(
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


@pytest.fixture(scope="function")
def db_name() -> str:
    """Return the name of a database."""
    return "hk_test.db"


@pytest.fixture(scope="function")
def db_path(db_dir: Path, db_name: str) -> Path:
    """Return the path to a database."""
    return db_dir / db_name


@pytest.fixture(scope="function")
def db_uri(db_path: Path) -> str:
    """Return the uri to an in memory database."""
    return "sqlite:///" + str(db_path)


@pytest.fixture(scope="function")
def db_uri_memory() -> str:
    """Return the uri to an in memory database."""
    return "sqlite:///:memory:"


@pytest.fixture(scope="function")
def configs(project_dir: Path, db_uri: str) -> dict:
    """Return a dict with housekeeper configs."""
    _configs = {"root": str(project_dir), "database": db_uri}
    return _configs


# object fixtures


@pytest.fixture(scope="function")
def vcf_tag_obj(vcf_tag_name: str, timestamp: datetime.datetime) -> str:
    """Return a tag object."""
    return Tag(name=vcf_tag_name, created_at=timestamp)


@pytest.fixture(scope="function")
def bundle_obj(bundle_data: dict, store: Store) -> Bundle:
    """Return a bundle object."""
    return store.add_bundle(bundle_data)[0]


@pytest.fixture(scope="function")
def sample_bundle(sample_bundle_data: dict, store: Store) -> Bundle:
    """Return a bundle object."""
    return store.add_bundle(sample_bundle_data)[0]


@pytest.fixture(scope="function")
def version_obj(bundle_data: dict, store: Store) -> Version:
    """Return a version object."""
    return store.add_bundle(bundle_data)[1]


@pytest.fixture(scope="function")
def archive(populated_store: Store) -> Archive:
    """Return an archive object."""
    return populated_store._get_query(table=Archive).first()


# dir fixtures


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return the path to the fixtures directory."""
    return Path("tests/fixtures/")


@pytest.fixture(scope="function")
def vcf_dir(fixtures_dir: Path) -> Path:
    """Return the path to the vcf fixtures directory."""
    return fixtures_dir / "vcfs"


@pytest.fixture(scope="session")
def sequencing_files_dir(fixtures_dir: Path) -> Path:
    """Return the path to the sequencing_files fixtures directory."""
    return Path(fixtures_dir, "sequencing_files")


@pytest.fixture(scope="function")
def project_dir(tmpdir_factory) -> Path:
    """Path to a temporary working directory."""
    my_tmpdir = Path(tmpdir_factory.mktemp("workdir"))
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


@pytest.fixture(scope="function")
def housekeeper_version_dir(project_dir: Path, case_id: str, timestamp_string: str) -> Path:
    """Path to a created directory with case and version."""
    hk_version_tmpdir: Path = Path(project_dir, case_id, timestamp_string)
    hk_version_tmpdir.mkdir(parents=True)
    return hk_version_tmpdir


@pytest.fixture(scope="function")
def config_dir(tmpdir_factory) -> Path:
    """Path to a temporary directory for config files."""
    my_tmpdir = Path(tmpdir_factory.mktemp("confdir"))
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


@pytest.fixture(scope="function")
def db_dir(tmpdir_factory) -> Path:
    """Path to a temporary directory for databases."""
    my_tmpdir = Path(tmpdir_factory.mktemp("db_dir"))
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


# File fixtures


@pytest.fixture(scope="function")
def config_file(config_dir: Path, configs: dict) -> Path:
    """Create a config file and return the path to it."""
    conf_path = config_dir / "config.json"
    with open(conf_path, "w") as out_file:
        yaml.dump(configs, out_file)
    return conf_path


@pytest.fixture(scope="function")
def sample_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return Path(vcf_dir, "example.vcf")


@pytest.fixture(scope="function")
def spring_file_1(sequencing_files_dir: Path) -> Path:
    """Return the path to a SPRING file."""
    return Path(sequencing_files_dir, "lane1.spring")


@pytest.fixture(scope="function")
def spring_file_2(sequencing_files_dir: Path) -> Path:
    """Return the path to a SPRING file."""
    return Path(sequencing_files_dir, "lane2.spring")


@pytest.fixture(scope="session")
def spring_file_3(sequencing_files_dir: Path) -> Path:
    """Return the path to a SPRING file."""
    return Path(sequencing_files_dir, "lane3.spring")


@pytest.fixture(scope="function")
def archived_file(spring_file_1: Path) -> Path:
    """Return the path to an archived file."""
    return spring_file_1


@pytest.fixture(scope="function")
def non_archived_file(spring_file_2: Path) -> Path:
    """Return the path to a non-archived file."""
    return spring_file_2


@pytest.fixture(scope="function")
def family_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return Path(vcf_dir, "family.vcf")


@pytest.fixture(scope="function")
def second_sample_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return Path(vcf_dir, "example.2.vcf")


@pytest.fixture(scope="function")
def second_family_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return Path(vcf_dir, "family.2.vcf")


@pytest.fixture(scope="function")
def third_family_vcf(vcf_dir: Path) -> Path:
    """Return the path to a vcf file."""
    return Path(vcf_dir, "family.3.vcf")


@pytest.fixture(scope="function")
def checksum_file(fixtures_dir: Path) -> Path:
    """Return the path to file to test checksum."""
    return Path(fixtures_dir, "26a90105b99c05381328317f913e9509e373b64f.txt")


@pytest.fixture(scope="function")
def checksum(checksum_file: Path) -> Path:
    """Return the checksum for checksum test file."""
    return checksum_file.name.rstrip(".txt")


# Store fixtures


@pytest.fixture(scope="function")
def store(project_dir: Path) -> Generator[Store, None, None]:
    """Return a store setup with all tables."""
    initialize_database("sqlite:///")
    _store = Store(root=str(project_dir))
    create_all_tables()
    yield _store
    drop_all_tables()


@pytest.fixture(scope="function")
def populated_store(
    archiving_task_id: int,
    new_archiving_task_id,
    retrieval_task_id: int,
    bundle_data: dict,
    helpers: Helpers,
    sample_bundle_data: dict,
    spring_file_1: Path,
    spring_file_3: Path,
    store: Store,
) -> Store:
    """Returns a populated store."""
    helpers.add_bundle(store=store, bundle=bundle_data)
    helpers.add_bundle(store=store, bundle=sample_bundle_data)
    helpers.add_archive(
        store=store,
        file_id=store.get_files(file_path=spring_file_1.as_posix()).first().id,
        archiving_task_id=archiving_task_id,
    )
    retrieval_archive: Archive = helpers.add_archive(
        store=store,
        file_id=store.get_files(file_path=spring_file_3.as_posix()).first().id,
        archiving_task_id=new_archiving_task_id,
    )
    retrieval_archive.retrieval_task_id = retrieval_task_id
    store.session.commit()

    return store
