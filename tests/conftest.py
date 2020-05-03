"""Base fixtures"""
import datetime
import shutil
from pathlib import Path

import dateutil
import pytest

from housekeeper import include
from housekeeper.store import Store, models

# basic fixtures


@pytest.fixture(scope="function", name="vcf_tag_name")
def fixture_vcf_tag_name() -> str:
    """Return a tag named 'vcf'"""
    return "vcf"


@pytest.fixture(scope="function", name="family_tag_name")
def fixture_family_tag_name() -> str:
    """Return a tag named 'family'"""
    return "family"


@pytest.fixture(scope="function", name="sample_tag_name")
def fixture_sample_tag_name() -> str:
    """Return a tag named 'sample'"""
    return "sample"


@pytest.fixture(scope="function", name="family_tag_names")
def fixture_family_tag_names(vcf_tag_name, family_tag_name) -> list:
    """Return a list of the family tag names"""
    return [vcf_tag_name, family_tag_name]


@pytest.fixture(scope="function", name="sample_tag_names")
def fixture_family_tags(vcf_tag_name, sample_tag_name) -> list:
    """Return a list of the sample tag names"""
    return [vcf_tag_name, sample_tag_name]


@pytest.fixture(scope="function", name="case_id")
def fixture_case_id() -> str:
    """Return name of a case"""
    return "handsomepig"


@pytest.fixture(scope="function", name="sample_data")
def fixture_sample_data(sample_tag_names, sample_vcf) -> str:
    """Return file and tags for sample"""
    return {"tags": sample_tag_names, "file": sample_vcf}


@pytest.fixture(scope="function", name="family_data")
def fixture_family_data(family_tag_names, family_vcf) -> str:
    """Return file and tags for sample"""
    return {"tags": family_tag_names, "file": family_vcf}


@pytest.fixture(scope="function", name="timestamp")
def fixture_timestamp() -> datetime.datetime:
    """Return a time stamp in date time format"""
    return datetime.datetime(2020, 5, 1)


@pytest.fixture(scope="function", name="bundle_data")
def fixture_bundle_data(case_id, sample_data, family_data, timestamp) -> dict:
    """Return a dummy bundle"""
    data = {
        "name": case_id,
        "created": timestamp,
        "expires": timestamp,
        "files": [
            {
                "path": str(sample_data["file"]),
                "archive": False,
                "tags": sample_data["tags"],
            },
            {
                "path": str(family_data["file"]),
                "archive": True,
                "tags": family_data["tags"],
            },
        ],
    }
    return data


# object fixtures


@pytest.fixture(scope="function", name="vcf_tag_obj")
def fixture_vcf_tag_obj(vcf_tag_name, timestamp) -> str:
    """Return a tag object"""
    return models.Tag(name=vcf_tag_name, created_at=timestamp)


@pytest.fixture(scope="function", name="bundle_obj")
def fixture_bundle_obj(bundle_data, store) -> str:
    """Return a bundle object"""
    return store.add_bundle(bundle_data)[0]


# dir fixtures


@pytest.fixture(scope="function", name="fixtures_dir")
def fixture_fixtures_dir() -> Path:
    """Return the path to the fixtures directory"""
    return Path("tests/fixtures/")


@pytest.fixture(scope="function", name="project_dir")
def fixture_project_dir(tmpdir_factory):
    """Path to a temporary working directory"""
    my_tmpdir = Path(tmpdir_factory.mktemp("workdir"))
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


# File fixtures


@pytest.fixture(scope="function", name="sample_vcf")
def fixture_sample_vcf(fixtures_dir) -> Path:
    """Return the path to a vcf file"""
    return fixtures_dir / "example.vcf"


@pytest.fixture(scope="function", name="family_vcf")
def fixture_family_vcf(fixtures_dir) -> Path:
    """Return the path to a vcf file"""
    return fixtures_dir / "family.vcf"


@pytest.fixture(scope="function", name="checksum_file")
def fixture_checksum_file(fixtures_dir) -> Path:
    """Return the path to file to test checksum"""
    return fixtures_dir / "26a90105b99c05381328317f913e9509e373b64f.txt"


@pytest.fixture(scope="function", name="checksum")
def fixture_checksum(checksum_file) -> Path:
    """Return the checksum for checksum test file"""
    return checksum_file.name.rstrip(".txt")


@pytest.fixture
def version(tmpdir):
    file_path_1 = tmpdir.join("example.vcf.gz")
    file_path_1.write("content")
    file_path_1_checksum = include.checksum(file_path_1)
    file_path_2 = tmpdir.join("example2.txt")
    file_path_2.write("content")
    bundle_obj = models.Bundle(name="privatefox")
    version_obj = models.Version(created_at=datetime.datetime.now(), bundle=bundle_obj)
    version_obj.files.append(
        models.File(
            path=file_path_1,
            to_archive=True,
            tags=[models.Tag(name="vcf-gz")],
            checksum=file_path_1_checksum,
        ),
    )
    version_obj.files.append(
        models.File(path=file_path_2, to_archive=False, tags=[models.Tag(name="tmp")])
    )
    return version_obj


@pytest.fixture(scope="function")
def bundle_data_old():
    data = {
        "name": "angrybird",
        "created": dateutil.parser.parse("2018/01/01 00:00:00"),
        "expires": datetime.datetime.now(),
        "files": [
            {
                "path": "tests/fixtures/example.2.vcf",
                "archive": False,
                "tags": ["vcf", "sample"],
            },
            {
                "path": "tests/fixtures/family.2.vcf",
                "archive": True,
                "tags": ["vcf", "family"],
            },
        ],
    }
    return data


# Store fixtures


@pytest.yield_fixture(scope="function", name="store")
def fixture_store(project_dir):
    """Return a store setup with all tables"""
    _store = Store(uri="sqlite://", root=str(project_dir))
    _store.create_all()
    yield _store
    _store.drop_all()


@pytest.yield_fixture(scope="function", name="populated_store")
def fixture_populated_store(store, bundle_data):
    """Returns a populated store"""
    bundle_obj = store.add_bundle(bundle_data)[0]
    store.add_commit(bundle_obj)
    return store
