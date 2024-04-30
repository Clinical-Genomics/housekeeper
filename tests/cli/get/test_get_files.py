"""Tests for cli get file functionality"""

from pathlib import Path

from housekeeper.cli.get import files_cmd
from housekeeper.services.file_report_service.utils import _get_suffix, squash_names
from housekeeper.store.models import File
from housekeeper.store.store import Store


def test_get_files_no_files(base_context, cli_runner):
    """Test to get all files when there are no files"""
    # GIVEN a context with a populated store and a cli runner
    store = base_context["store"]

    # GIVEN a store without files
    assert not store.get_files().all()

    # WHEN fetching all files by not specifying any file
    result = cli_runner.invoke(files_cmd, ["--json"], obj=base_context)

    # THEN assert that output was produced
    assert result.exit_code == 0


def test_get_files_json(populated_context, cli_runner):
    """Test to get all files from a populated store"""
    # GIVEN a context
    store: Store = populated_context["store"]

    # GIVEN a store with files
    files: list[File] = store.get_files()

    # WHEN fetching all files
    result = cli_runner.invoke(files_cmd, ["--json"], obj=populated_context)

    # THEN assert that all files where printed
    for file in files:
        assert file.path in result.output


def test_get_files(populated_context, cli_runner):
    """Test to get all files from a populated store in human friendly format"""
    # GIVEN a context and a store
    store: Store = populated_context["store"]

    # GIVEN a store with some files
    assert store.get_files().all()

    # GIVEN a file name
    file: File = store.get_files().first()
    file_name: str = Path(file.path).name

    # WHEN fetching all files by not specifying any file
    result = cli_runner.invoke(files_cmd, [], obj=populated_context)

    # THEN assert that the file name is displayed
    assert file_name in result.output

    # THEN assert that the full file path is not shown
    assert file.path not in result.output


def test_get_files_tag(populated_context, cli_runner, vcf_tag_name):
    """Test to get files with a specific tag from a populated store"""
    # GIVEN a context with a populated store
    store: Store = populated_context["store"]

    # GIVEN a store with some files that are tagged
    tagged_files: list[File] = store.get_files(tag_names=[vcf_tag_name]).all()
    assert tagged_files

    # WHEN fetching all files by not specifying any file
    result = cli_runner.invoke(files_cmd, ["--tag", vcf_tag_name, "--json"], obj=populated_context)

    # THEN assert that all files where fetched
    for file in tagged_files:
        assert file.path in result.output


def test_get_files_multiple_tags(populated_context, cli_runner, vcf_tag_name, family_tag_name):
    """Test to get files with multiple tags tag from a populated store"""
    # GIVEN a context with a populated store
    store: Store = populated_context["store"]

    # GIVEN a store with some files that are tagged
    files: list[File] = store.get_files(tag_names=[vcf_tag_name, family_tag_name]).all()
    assert files

    # WHEN fetching all files by not specifying any file
    result = cli_runner.invoke(
        files_cmd,
        ["--tag", vcf_tag_name, "--tag", family_tag_name, "--json"],
        obj=populated_context,
    )

    # THEN assert that all files where fetched
    for file in files:
        assert file.path in result.output


def test_get_files_rare_tag(populated_context, cli_runner, family_tag_name):
    """Test to get files with a tag that is not on all files from a populated store"""
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a store with some tagged files
    tagged_files: list[File] = store.get_files(tag_names=[family_tag_name]).all()

    # WHEN fetching all tagged files
    result = cli_runner.invoke(
        files_cmd, ["--tag", family_tag_name, "--json"], obj=populated_context
    )

    # THEN all tagged files where fetched
    for tagged_file in tagged_files:
        assert tagged_file.path in result.output


def test_get_files_compact():
    """Test to get all files from a populated store in human friendly format, subsequent names concatenated"""
    # GIVEN an example result file list
    file_list = [
        {"path": "family.vcf", "full_path": "tests/family.vcf", "tags": [], "id": 7},
        {
            "path": "family.2.vcf",
            "full_path": "/tests/family.2.vcf",
            "tags": [],
            "id": 8,
        },
        {
            "path": "family.3.vcf",
            "full_path": "/tests/family.3.vcf",
            "tags": [],
            "id": 9,
        },
    ]

    # WHEN calling `squash_names` on list of files
    squashed = squash_names(file_list)

    # THEN assert that the file names displayed are squashed
    assert len(squashed) < len(file_list)


def test_get_suffix():
    # GIVEN
    dont_split_name1 = "asdf2.asdf.vcf"
    dont_split_name2 = "1123"
    dont_split_name3 = "asdf.vcf"
    dont_split_name4 = "asdf_2.asdf.vcf"

    split_name1 = "asdf1.png"
    split_name2 = "asdf8A8_7777_asdf_8.png"

    # THEN assert filename parsing *does not* split name into (prefix, integer, suffix)
    assert (dont_split_name1, "", "") == _get_suffix(dont_split_name1)
    assert (dont_split_name2, "", "") == _get_suffix(dont_split_name2)
    assert (dont_split_name3, "", "") == _get_suffix(dont_split_name3)
    assert (dont_split_name4, "", "") == _get_suffix(dont_split_name4)

    # THEN assert filename parsing *does* split name into (prefix, integer, suffix)
    assert (split_name1, "", "") != _get_suffix(split_name1)
    assert (split_name2, "", "") != _get_suffix(split_name2)
