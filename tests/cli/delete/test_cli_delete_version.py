"""Tests for delete version CLI functions"""
import logging
from click import Context
from click.testing import CliRunner

from housekeeper.cli import delete


def test_delete_non_version_no_input(base_context: Context, cli_runner: CliRunner, caplog):
    """Test to delete a version without any input

    The command should fail since there is no input
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner

    # WHEN trying to delete a version without specifying anything
    result = cli_runner.invoke(delete.version_cmd, [], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the bundle was not found
    assert "Please select a bundle or a version" in caplog.text


# def test_delete_existing_bundle_with_version(
#     populated_context: Context, cli_runner: CliRunner, case_id: str, caplog
# ):
#     """Test to delete an existing bundle with versions"""
#     caplog.set_level(logging.DEBUG)
#     # GIVEN a context with a store and a cli runner
#     store = populated_context["store"]
#     # GIVEN a bundle with versions
#     bundle_obj = store.bundle(name=case_id)
#     assert len(bundle_obj.versions) > 0
#
#     # WHEN trying to delete a bundle
#     result = cli_runner.invoke(delete.bundle_cmd, [case_id], obj=populated_context)
#
#     # THEN it should ask if you are sure
#     assert "Bundle has versions, can not delete bundle" in caplog.text
#
#
# def test_delete_existing_bundle_no_versions_no_confirmation(
#     populated_context: Context, cli_runner: CliRunner, case_id: str, caplog
# ):
#     """Test to delete an existing bundle without confirmation"""
#     caplog.set_level(logging.DEBUG)
#     # GIVEN a context with a store and a cli runner
#     store = populated_context["store"]
#     # GIVEN a bundle without versions
#     cli_runner.invoke(delete.version_cmd, ["-b", case_id], obj=populated_context, input="Yes")
#     bundle_obj = store.bundle(name=case_id)
#     assert len(bundle_obj.versions) == 0
#
#     # WHEN trying to delete a bundle
#     result = cli_runner.invoke(delete.bundle_cmd, [case_id], obj=populated_context, input="no")
#     # THEN assert it exits non zero
#     assert result.exit_code == 1
#
#
# def test_delete_existing_bundle_no_versions_with_confirmation(
#     populated_context: Context, cli_runner: CliRunner, case_id: str, caplog
# ):
#     """Test to delete an existing bundle without confirmation"""
#     caplog.set_level(logging.DEBUG)
#     # GIVEN a context with a store and a cli runner
#     store = populated_context["store"]
#     # GIVEN a bundle without versions
#     cli_runner.invoke(delete.version_cmd, ["-b", case_id], obj=populated_context, input="Yes")
#     bundle_obj = store.bundle(name=case_id)
#     assert len(bundle_obj.versions) == 0
#
#     # WHEN trying to delete a bundle
#     result = cli_runner.invoke(delete.bundle_cmd, [case_id], obj=populated_context, input="Yes")
#     # THEN assert it exits non zero
#     assert result.exit_code == 0
#     # THEN it should communicate that it was deleted
#     assert "Bundle deleted" in caplog.text
