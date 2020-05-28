"""Tests for cli get file functionality"""
from pathlib import Path

from housekeeper.cli.get import files_cmd


def test_get_files_no_files(base_context, cli_runner, helpers):
    """Test to get all files when there are no files"""
    # GIVEN a context with a populated store and a cli runner
    store = base_context["store"]
    # GIVEN a store without files
    assert helpers.count_iterable(store.files()) == 0

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
    store = populated_context["store"]
    # GIVEN a store with some files
    nr_files = helpers.count_iterable(store.files())
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
    store = populated_context["store"]
    # GIVEN a file name
    file_obj = store.files().first()
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
    store = populated_context["store"]
    # GIVEN a store with some files that are tagged
    nr_files = helpers.count_iterable(store.files(tags=[vcf_tag_name]))
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
    store = populated_context["store"]
    # GIVEN a store with some files that are tagged
    nr_files = helpers.count_iterable(store.files(tags=[vcf_tag_name, family_tag_name]))
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
    store = populated_context["store"]
    # GIVEN a store with some files that are tagged
    total_nr_files = helpers.count_iterable(store.files())
    nr_tag_files = helpers.count_iterable(store.files(tags=[family_tag_name]))
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
