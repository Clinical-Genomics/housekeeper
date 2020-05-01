"""Base fixtures"""
import datetime
import shutil
from pathlib import Path

import dateutil
import pytest

from housekeeper import include
from housekeeper.store import Store, models

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


@pytest.fixture(scope="function", name="bundle_data")
def fixture_bundle_data(sample_vcf, family_vcf) -> dict:
    """Return a dummy bundle"""
    data = {
        "name": "sillyfish",
        "created": datetime.datetime.now(),
        "expires": datetime.datetime.now(),
        "files": [
            {"path": str(sample_vcf), "archive": False, "tags": ["vcf", "sample"]},
            {"path": str(family_vcf), "archive": True, "tags": ["vcf", "family"]},
        ],
    }
    return data


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


@pytest.fixture(scope="function")
def rna_bundle_data_one_file():
    """test fixture"""
    data = {
        "name": "finequagga",
        "created": datetime.datetime.now(),
        "expires": datetime.datetime.now(),
        "files": [
            {
                "path": "tests/fixtures/example.vcf",
                "archive": False,
                "tags": ["vcf", "sample"],
            }
        ],
    }
    return data


@pytest.fixture(scope="function")
def rna_bundle_data_two_files():
    """test fixture"""
    data = {
        "name": "finequagga",
        "created": datetime.datetime.now(),
        "expires": datetime.datetime.now(),
        "files": [
            {
                "path": ["tests/fixtures/example.vcf", "tests/fixtures/example.2.vcf"],
                "archive": False,
                "tags": ["vcf", "sample"],
            }
        ],
    }
    return data


@pytest.yield_fixture(scope="function")
def store(tmpdir):
    _store = Store(uri="sqlite://", root=str(tmpdir))
    _store.create_all()
    yield _store
    _store.drop_all()
