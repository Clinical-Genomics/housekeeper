"""Tests for adding versions via CLI"""

import json
import logging

from click import Context
from click.testing import CliRunner

from housekeeper.cli.add import version_cmd
from housekeeper.store.models import Bundle
from housekeeper.store.store import Store


def test_add_version_non_input(populated_context: Context, cli_runner: CliRunner, caplog):
    """Test to add a version to a bundle without providing input

    The CLI should exit with non zero since nothing is defined
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner

    # WHEN trying to add a version to a non existing bundle
    result = cli_runner.invoke(version_cmd, [], obj=populated_context)

    # THEN assert it has a non zero exit status
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert "Please input json or bundle_name" in caplog.text


def test_add_version_non_existing_bundle(populated_context: Context, cli_runner: CliRunner, caplog):
    """Test to add a version to a non existing bundle

    The CLI should exit with non zero since the bundle does not exist
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a non existing bundle
    bundle_name = "non_existing"
    bundle: Bundle = store.get_bundle_by_name(bundle_name=bundle_name)
    assert not bundle

    # WHEN trying to add a version to a non existing bundle
    result = cli_runner.invoke(version_cmd, [bundle_name], obj=populated_context)

    # THEN assert it has a non zero exit status
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert f"unknown bundle: {bundle_name}" in caplog.text


def test_add_version_existing_bundle(populated_context: Context, cli_runner: CliRunner, caplog):
    """Test to add a version to a existing bundle

    The functionality should work as expected since the bundle exists
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a existing bundle
    bundle: Bundle = store._get_query(table=Bundle).first()
    assert isinstance(bundle, Bundle)

    # GIVEN the name of a existing bundle
    bundle_name: str = bundle.name

    # WHEN trying to add a version to an existing bundle
    result = cli_runner.invoke(version_cmd, [bundle_name], obj=populated_context)

    # THEN assert it has a zero exit status
    assert result.exit_code == 0
    # THEN check that the error message is displayed
    assert f"added to bundle {bundle_name}" in caplog.text
    assert "new version" in caplog.text


def test_add_version_existing_bundle_same_date(
    populated_context: Context, cli_runner: CliRunner, timestamp_string: str, caplog
):
    """Test to add a version to an existing bundle when the date is the same

    It should not be possible to add two versions with the same dates
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a existing bundle
    bundle: Bundle = store._get_query(table=Bundle).first()
    assert isinstance(bundle, Bundle)
    bundle_name: str = bundle.name

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
    populated_context: Context,
    cli_runner: CliRunner,
    empty_version_data_json: str,
    caplog,
):
    """Test to add a new empty version to existing bundle using json as input

    This should work since there is no problem to add a version without files
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store a cli runner
    store: Store = populated_context["store"]
    version_data = json.loads(empty_version_data_json)
    # GIVEN a bundle with one version
    bundle = store.get_bundle_by_name(bundle_name=version_data["bundle_name"])
    assert isinstance(bundle, Bundle)
    assert len(bundle.versions) == 1
    # GIVEN version information without files, in json format
    assert version_data["files"] == []

    # WHEN trying to add the version
    result = cli_runner.invoke(
        version_cmd, ["--json", empty_version_data_json], obj=populated_context
    )

    # THEN assert it succeded
    assert result.exit_code == 0
    # THEN check that the error message is displayed
    assert f"added to bundle {version_data['bundle_name']}" in caplog.text
    assert "new version" in caplog.text
    # THEN assert that the version was added
    bundle = store.get_bundle_by_name(bundle_name=version_data["bundle_name"])
    assert len(bundle.versions) == 2


def test_add_version_with_files_json(
    populated_context: Context, cli_runner: CliRunner, version_data_json: str, caplog
):
    """Test to add a new version with files to existing bundle using json as input"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store a cli runner
    store: Store = populated_context["store"]
    version_data = json.loads(version_data_json)
    # GIVEN a bundle with one version
    bundle = store.get_bundle_by_name(bundle_name=version_data["bundle_name"])
    assert isinstance(bundle, Bundle)
    assert len(bundle.versions) == 1
    # GIVEN version information without files, in json format
    assert version_data["files"] != []

    # WHEN trying to add the version
    result = cli_runner.invoke(version_cmd, ["--json", version_data_json], obj=populated_context)

    # THEN assert it succeded
    assert result.exit_code == 0
    # THEN check that the error message is displayed
    assert f"added to bundle {version_data['bundle_name']}" in caplog.text
    assert "new version" in caplog.text
    # THEN assert that the files where added to the version was added
    bundle = store.get_bundle_by_name(bundle_name=version_data["bundle_name"])
    for version_obj in bundle.versions:
        assert len(version_obj.files) == 2


def test_add_version_with_json_and_bundle_name(
    populated_context, cli_runner, version_data_json: str, caplog
):
    """Test to add a new version to existing bundle using both json and bundle_name as input

    The CLI should fail since it is ambiguous to specify the bundle in two ways
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store a cli runner and a dummy bundle name
    bundle_name = "hello"

    # WHEN trying to add the version
    result = cli_runner.invoke(
        version_cmd, [bundle_name, "--json", version_data_json], obj=populated_context
    )

    # THEN assert it succeded
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert "Can not input both json and bundle_name" in caplog.text
