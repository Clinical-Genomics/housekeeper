"""Tests for delete CLI functions"""

from click import Context
from click.testing import CliRunner

from housekeeper.cli import delete


def test_delete_non_existing_bundle(base_context: Context, cli_runner: CliRunner):
    """Test to delete a non existing bundle"""
    # GIVEN a context with a store and a cli runner
    # GIVEN a case name that does not exist
    case_name = "hello"
    assert not base_context["store"].bundle(name=case_name)

    # WHEN trying to delete a non existing bundle
    result = cli_runner.invoke(delete.bundle_cmd, [case_name], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the bundle was not found
    assert "bundle not found" in result.output


def test_delete_existing_bundle_with_confirmation(
    populated_context: Context, cli_runner: CliRunner, case_id: str
):
    """Test to delete an existing bundle"""
    # GIVEN a context with a store and a cli runner

    # WHEN trying to delete a bundle
    result = cli_runner.invoke(delete.bundle_cmd, [case_id], obj=populated_context)
    # THEN it should ask if you are sure
    assert "remove bundle version from" in result.output


def test_delete_existing_bundle_no_confirmation(populated_context, cli_runner, case_id):
    """Test to delete an existing bundle without confirmation"""
    # GIVEN a context with a store and a cli runner
    # WHEN trying to delete a bundle
    result = cli_runner.invoke(delete.bundle_cmd, [case_id], obj=populated_context, input="Yes")
    # THEN assert it exits non zero
    assert result.exit_code == 0
    # THEN it should communicate that it was deleted
    assert "version deleted:" in result.output
