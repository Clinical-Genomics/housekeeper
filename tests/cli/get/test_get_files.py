"""Tests for cli get file functionality"""
from pathlib import Path
from housekeeper.cli.get import files_cmd
from housekeeper.cli.tables import squash_names, _get_suffix
from housekeeper.store.api.core import Store


def test_get_files_no_files(base_context, cli_runner, helpers):
    """Test to get all files when there are no files"""
    # GIVEN a context with a populated store and a cli runner
    store = base_context["store"]
    # GIVEN a store without files
    assert helpers.count_iterable(store.get_files()) == 0

    # WHEN fetching all files by not specifying any file
    json_bundles = helpers.get_json(
        cli_runner.invoke(files_cmd, ["--json"], obj=base_context).output
    )

    # THEN assert that we get a list
    assert isinstance(json_bundles, list)
    # THEN assert that no files where fetched
    assert len(json_bundles) == 0


def test_get_files_json(populated_context, cli_runner, helpers):
    """Test to get all files from a populated store"""
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a store with some files
    nr_files = helpers.count_iterable(store.get_files())
    assert nr_files > 0

    # WHEN fetching all files by not specifying any file
    json_bundles = helpers.get_json(
        cli_runner.invoke(files_cmd, ["--json"], obj=populated_context).output
    )

    # THEN assert that all files where fetched
    assert len(json_bundles) == nr_files


def test_get_files(populated_context, cli_runner):
    """Test to get all files from a populated store in human friendly format"""
    # GIVEN a context with a populated store and a cli runner
    # GIVEN a store with some files
    store: Store = populated_context["store"]
    # GIVEN a file name
    file_obj = store.get_files().first()
    file_name = Path(file_obj.path).name

    # WHEN fetching all files by not specifying any file
    result = cli_runner.invoke(files_cmd, [], obj=populated_context)

    # THEN assert that the file name of one file is displayed
    assert file_name in result.output
    # THEN assert that the full file path is not shown
    assert file_obj.path not in result.output


def test_get_files_tag(populated_context, cli_runner, helpers, vcf_tag_name):
    """Test to get files with a specific tag from a populated store"""
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a store with some files that are tagged
    nr_files = helpers.count_iterable(store.get_files(tag_names=[vcf_tag_name]))
    assert nr_files > 0

    # WHEN fetching all files by not specifying any file
    json_bundles = helpers.get_json(
        cli_runner.invoke(
            files_cmd, ["--tag", vcf_tag_name, "--json"], obj=populated_context
        ).output
    )

    # THEN assert that all files where fetched
    assert len(json_bundles) == nr_files


def test_get_files_multiple_tags(
    populated_context, cli_runner, helpers, vcf_tag_name, family_tag_name
):
    """Test to get files with multiple tags tag from a populated store"""
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a store with some files that are tagged
    nr_files = helpers.count_iterable(store.get_files(tag_names=[vcf_tag_name, family_tag_name]))
    assert nr_files > 0

    # WHEN fetching all files by not specifying any file
    json_bundles = helpers.get_json(
        cli_runner.invoke(
            files_cmd,
            ["--tag", vcf_tag_name, "--tag", family_tag_name, "--json"],
            obj=populated_context,
        ).output
    )

    # THEN assert that all files where fetched
    assert len(json_bundles) == nr_files


def test_get_files_rare_tag(populated_context, cli_runner, helpers, family_tag_name):
    """Test to get files with a tag that is not on all files from a populated store"""
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a store with some files that are tagged
    total_nr_files = helpers.count_iterable(store.get_files())
    nr_tag_files = helpers.count_iterable(store.get_files(tag_names=[family_tag_name]))
    # GIVEN a tag that only fetches a subset of the files
    assert nr_tag_files < total_nr_files

    # WHEN fetching all files with that tag
    json_bundles = helpers.get_json(
        cli_runner.invoke(
            files_cmd, ["--tag", family_tag_name, "--json"], obj=populated_context
        ).output
    )

    # THEN assert that all files where fetched
    assert len(json_bundles) == nr_tag_files


def test_get_files_compact(populated_context_subsequent, cli_runner, family_tag_name, helpers):
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
