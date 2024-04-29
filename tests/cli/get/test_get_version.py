"""Tests for get version CLI functionality"""

import logging

from click import Context
from click.testing import CliRunner

from housekeeper.cli.get import version_cmd
from housekeeper.store.models import Bundle, Version
from housekeeper.store.store import Store


def test_get_version_no_input(populated_context: Context, cli_runner: CliRunner, caplog):
    """Test to get all versions when no input is given

    This should exit with False
    """
    caplog.set_level(logging.DEBUG)

    # GIVEN a context that is populated
    # WHEN running the get versions command
    result = cli_runner.invoke(version_cmd, [], obj=populated_context)

    # THEN assert that the program exits with a zero exit code
    assert result.exit_code == 0
    # THEN assert that the correct information is communicated
    assert "Please select a bundle or a version" in caplog.text


def test_get_version_bundle_name(populated_context: Context, cli_runner: CliRunner, helpers):
    """Test to get all versions from a bundle by using the bundle name.

    This should return all versions
    """
    # GIVEN a context that is populated
    store: Store = populated_context["store"]
    bundle_obj: Bundle = store._get_query(table=Bundle).first()
    version_obj: Version = bundle_obj.versions[0]
    bundle_name: str = bundle_obj.name

    # WHEN running the include files command
    result = cli_runner.invoke(version_cmd, ["-b", bundle_name], obj=populated_context)

    # THEN assert that the version path was created
    assert str(version_obj.id) in result.output


def test_get_version_non_existing_bundle_name(
    populated_context: Context, cli_runner: CliRunner, caplog
):
    """
    Test to get all versions from a bundle that does not exist
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context that is populated
    store: Store = populated_context["store"]
    # GIVEN a non existing bundle name
    bundle_name = "hello"
    assert not store.get_bundle_by_name(bundle_name=bundle_name)

    # WHEN running the include files command
    cli_runner.invoke(version_cmd, ["-b", bundle_name], obj=populated_context)

    # THEN assert that the correct information is communicated
    assert f"Could not find bundle {bundle_name}" in caplog.text


def test_get_version_json(populated_context: Context, cli_runner: CliRunner, helpers):
    """Test to get all versions from a bundle by using the bundle name in json format.

    This should return all versions
    """
    # GIVEN a context that is populated
    store: Store = populated_context["store"]
    bundle_obj = store._get_query(table=Bundle).first()
    bundle_name = bundle_obj.name

    # WHEN running the include files command
    result = cli_runner.invoke(version_cmd, ["-b", bundle_name, "--json"], obj=populated_context)

    # THEN assert that the program exits succesfully
    assert result.exit_code == 0


def test_get_version_version_id(populated_context: Context, cli_runner: CliRunner, helpers):
    """Test to get all versions from a bundle by using the bundle name in json format.

    This should return all versions
    """
    # GIVEN a context that is populated
    store: Store = populated_context["store"]
    bundle_obj: Bundle = store._get_query(table=Bundle).first()
    version_obj: Version = bundle_obj.versions[0]
    version_id: int = version_obj.id

    # WHEN running the include files command
    result = cli_runner.invoke(version_cmd, ["-i", version_id], obj=populated_context)

    # THEN assert that the program exits succesfully
    assert result.exit_code == 0
