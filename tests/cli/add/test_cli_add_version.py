"""Tests for adding versions via CLI"""
import json
import logging

from housekeeper.cli.add import version_cmd


def test_add_version_non_existing_bundle(populated_context, cli_runner, caplog):
    """Test to add a version to a non existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a non existing bundle
    bundle_name = "non_existing"
    bundle_obj = store.bundle(bundle_name)
    assert not bundle_obj

    # WHEN trying to add a version to a non existing bundle
    result = cli_runner.invoke(version_cmd, [bundle_name], obj=populated_context)

    # THEN assert it has a non zero exit status
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert f"unknown bundle: {bundle_name}" in caplog.text


def test_add_version_existing_bundle(populated_context, cli_runner, caplog):
    """Test to add a version to a existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    bundle_name = bundle_obj.name

    # WHEN trying to add a version to an existing bundle
    result = cli_runner.invoke(version_cmd, [bundle_name], obj=populated_context)

    # THEN assert it has a zero exit status
    assert result.exit_code == 0
    # THEN check that the error message is displayed
    assert f"added to bundle {bundle_name}" in caplog.text
    assert "new version" in caplog.text


def test_add_version_existing_bundle_same_date(
    populated_context, cli_runner, caplog, timestamp_string
):
    """Test to add a version to an existing bundle when the date is the same

    It should not be possible to add two versions with the same dates
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    bundle_name = bundle_obj.name

    # WHEN trying to add a version to an existing bundle
    result = cli_runner.invoke(
        version_cmd,
        [bundle_name, "--created-at", timestamp_string],
        obj=populated_context,
    )

    # THEN assert it has a non zero exit status
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert "version of bundle already added" in caplog.text


def test_add_version_no_files_json(
    populated_context, cli_runner, empty_version_data_json, caplog
):
    """Test to add a new empty version to existing bundle using json as input"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store a cli runner
    store = populated_context["store"]
    version_data = json.loads(empty_version_data_json)
    # GIVEN a bundle with one version
    bundle_obj = store.bundle(version_data["bundle_name"])
    assert bundle_obj
    assert len(bundle_obj.versions) == 1
    # GIVEN version information without files, in json format
    assert version_data["files"] == []

    # WHEN trying to add the version
    result = cli_runner.invoke(
        version_cmd, [empty_version_data_json, "--json"], obj=populated_context
    )

    # THEN assert it succeded
    assert result.exit_code == 0
    # THEN check that the error message is displayed
    assert f"added to bundle {version_data['bundle_name']}" in caplog.text
    assert "new version" in caplog.text
    # THEN assert that the version was added
    bundle_obj = store.bundle(version_data["bundle_name"])
    assert len(bundle_obj.versions) == 2


#
# def test_add_bundle_json_no_files(base_context, cli_runner, bundle_data_json, caplog):
#     """Test to add a new bundle using json as input but no files. It should be possible to add
#     a bundle without any files
#     """
#     caplog.set_level(logging.DEBUG)
#     # GIVEN a context with a empty store, a cli runner and a bundle in json format without files
#     bundle_data = json.loads(bundle_data_json)
#     bundle_data.pop("files")
#     bundle_data_json = json.dumps(bundle_data)
#
#     # WHEN trying to add a bundle
#     result = cli_runner.invoke(
#         bundle_cmd, [bundle_data_json, "--json"], obj=base_context
#     )
#
#     # THEN assert it succeded
#     assert result.exit_code == 0
#     # THEN check that the proper information is displayed even if there where no files added
#     assert "new bundle added" in caplog.text
#
#
# def test_add_bundle_non_existing_file(
#     base_context, cli_runner, bundle_data_json, caplog
# ):
#     """Test to add a new bundle using json as input when some files does not exist.
#
#     The program should exit with a non zero exit code since a file is missing
#     """
#     caplog.set_level(logging.DEBUG)
#     # GIVEN a context with a empty store, a cli runner and a bundle in json format with non
#     # existing files
#     non_existing = "a_non_existing_file.txt"
#     bundle_data = json.loads(bundle_data_json)
#     bundle_data["files"][0]["path"] = non_existing
#     bundle_data_json = json.dumps(bundle_data)
#
#     # WHEN trying to add a bundle
#     result = cli_runner.invoke(
#         bundle_cmd, [bundle_data_json, "--json"], obj=base_context
#     )
#
#     # THEN assert it succeded
#     assert result.exit_code == 1
#     # THEN check that the proper information is displayed
#     assert f"File {non_existing} does not exist" in caplog.text
#
#
# def test_add_bundle_json_missing_data(
#     base_context, cli_runner, bundle_data_json, caplog
# ):
#     """Test to add a new bundle using json as input but no date. It is mandatory to have a
#         created_at date.
#     """
#     caplog.set_level(logging.DEBUG)
#     # GIVEN a context with a empty store, a cli runner and a bundle in json format without files
#     bundle_data = json.loads(bundle_data_json)
#     bundle_data.pop("created_at")
#     bundle_data_json = json.dumps(bundle_data)
#
#     # WHEN trying to add a bundle
#     result = cli_runner.invoke(
#         bundle_cmd, [bundle_data_json, "--json"], obj=base_context
#     )
#
#     # THEN assert it succeded
#     assert result.exit_code == 1
#     # THEN check that the proper information is displayed even if there where no files added
#     assert "Bundle date is required" in caplog.text
