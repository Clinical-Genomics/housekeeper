"""Tests for adding bundles via CLI"""
import json
import logging

from housekeeper.cli.add import bundle_cmd


def test_add_existing_bundle(populated_context, cli_runner, caplog):
    """Test to add a bundle that exists"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    bundle_name = bundle_obj.name

    # WHEN trying to add a bundle that exists
    result = cli_runner.invoke(bundle_cmd, [bundle_name], obj=populated_context)

    # THEN assert it has a non zero exit status
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert "already exists" in caplog.text


def test_add_simple_bundle(base_context, cli_runner, case_id, caplog):
    """Test to add a new bundle by only specifying bundle name"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store and a cli runner
    bundle_name = case_id

    # WHEN trying to add a bundle with only the bundle name
    result = cli_runner.invoke(bundle_cmd, [bundle_name], obj=base_context)

    # THEN assert it succeded
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert "new bundle added" in caplog.text


def test_add_bundle_json(base_context, cli_runner, bundle_data_json, caplog):
    """Test to add a new bundle using json as input"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store, a cli runner and a bundle in json format
    # WHEN trying to add a bundle
    result = cli_runner.invoke(
        bundle_cmd, [bundle_data_json, "--json"], obj=base_context
    )

    # THEN assert it succeded
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert "new bundle added" in caplog.text


def test_add_bundle_json_no_files(base_context, cli_runner, bundle_data_json, caplog):
    """Test to add a new bundle using json as input but no files. It should be possible to add
    a bundle without any files
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store, a cli runner and a bundle in json format without files
    bundle_data = json.loads(bundle_data_json)
    bundle_data.pop("files")
    bundle_data_json = json.dumps(bundle_data)

    # WHEN trying to add a bundle
    result = cli_runner.invoke(
        bundle_cmd, [bundle_data_json, "--json"], obj=base_context
    )

    # THEN assert it succeded
    assert result.exit_code == 0
    # THEN check that the proper information is displayed even if there where no files added
    assert "new bundle added" in caplog.text


def test_add_bundle_non_existing_file(
    base_context, cli_runner, bundle_data_json, caplog
):
    """Test to add a new bundle using json as input when some files does not exist.

    The program should exit with a non zero exit code since a file is missing
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store, a cli runner and a bundle in json format with non
    # existing files
    non_existing = "a_non_existing_file.txt"
    bundle_data = json.loads(bundle_data_json)
    bundle_data["files"][0]["path"] = non_existing
    bundle_data_json = json.dumps(bundle_data)

    # WHEN trying to add a bundle
    result = cli_runner.invoke(
        bundle_cmd, [bundle_data_json, "--json"], obj=base_context
    )

    # THEN assert it succeded
    assert result.exit_code == 1
    # THEN check that the proper information is displayed
    assert f"File {non_existing} does not exist" in caplog.text


def test_add_bundle_json_missing_data(
    base_context, cli_runner, bundle_data_json, caplog
):
    """Test to add a new bundle using json as input but no date. It is mandatory to have a
        created_at date.
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store, a cli runner and a bundle in json format without files
    bundle_data = json.loads(bundle_data_json)
    bundle_data.pop("created_at")
    bundle_data_json = json.dumps(bundle_data)

    # WHEN trying to add a bundle
    result = cli_runner.invoke(
        bundle_cmd, [bundle_data_json, "--json"], obj=base_context
    )

    # THEN assert it succeded
    assert result.exit_code == 1
    # THEN check that the proper information is displayed even if there where no files added
    assert "Bundle date is required" in caplog.text
