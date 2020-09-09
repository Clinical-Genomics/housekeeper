"""Tests for get version CLI functionality"""
import logging
import json

from datetime import datetime
from click import Context
from click.testing import CliRunner

from housekeeper.cli.get import version_cmd


def test_get_version_bundle_name(populated_context: Context, cli_runner: CliRunner, helpers):
    """Test to get all versions from a bundle by using the bundle name.

    This should return all versions
    """
    # GIVEN a context that is populated
    store = populated_context["store"]
    bundle_obj = store.Bundle.query.first()
    version_obj = bundle_obj.versions[0]
    bundle_name = bundle_obj.name

    # WHEN running the include files command
    result = cli_runner.invoke(version_cmd, ["-b", bundle_name], obj=populated_context)

    # THEN assert that the version path was created
    assert str(version_obj.id) in result.output


# def test_get_version_json(
#     populated_context: Context, cli_runner: CliRunner, helpers
# ):
#     """Test to get all versions from a bundle by using the bundle name in json format.
#
#     This should return all versions
#     """
#     # GIVEN a context that is populated
#     store = populated_context["store"]
#     bundle_obj = store.Bundle.query.first()
#     version_obj = bundle_obj.versions[0]
#     bundle_name = bundle_obj.name
#
#     # WHEN running the include files command
#     result = cli_runner.invoke(version_cmd, ["-b", bundle_name, "--json"], obj=populated_context)
#     json_output = json.loads(result.output)
#
#     # THEN assert that the version path was created
#     assert json_output[0]["id"] == version_obj.id
#
