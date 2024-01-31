"""Tests for delete CLI functions"""

import logging

from click import Context
from click.testing import CliRunner

from housekeeper.cli import delete
from housekeeper.store.store import Store


def test_delete_non_existing_bundle(base_context: Context, cli_runner: CliRunner, caplog):
    """Test to delete a non existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner
    # GIVEN a case name that does not exist
    case_name = "hello"
    assert not base_context["store"].get_bundle_by_name(bundle_name=case_name)

    # WHEN trying to delete a non existing bundle
    result = cli_runner.invoke(delete.bundle_cmd, [case_name], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the bundle was not found
    assert f"bundle {case_name} not found" in caplog.text


def test_delete_existing_bundle_with_version(
    populated_context: Context, cli_runner: CliRunner, case_id: str, caplog
):
    """Test to delete an existing bundle with versions"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a bundle with versions
    bundle_obj = store.get_bundle_by_name(bundle_name=case_id)
    assert len(bundle_obj.versions) > 0

    # WHEN trying to delete a bundle
    cli_runner.invoke(delete.bundle_cmd, [case_id], obj=populated_context)

    # THEN it should ask if you are sure
    assert "Can not delete bundle, please remove all versions first" in caplog.text


def test_delete_existing_bundle_no_versions_no_confirmation(
    populated_context: Context, cli_runner: CliRunner, case_id: str, caplog
):
    """Test to delete an existing bundle without confirmation"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a bundle without versions
    cli_runner.invoke(delete.version_cmd, ["-b", case_id], obj=populated_context, input="Yes")
    bundle_obj = store.get_bundle_by_name(bundle_name=case_id)
    assert len(bundle_obj.versions) == 0

    # WHEN trying to delete a bundle
    result = cli_runner.invoke(delete.bundle_cmd, [case_id], obj=populated_context, input="no")
    # THEN assert it exits non zero
    assert result.exit_code == 1


def test_delete_existing_bundle_no_versions_with_confirmation(
    populated_context: Context, cli_runner: CliRunner, case_id: str, caplog
):
    """Test to delete an existing bundle without confirmation"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a bundle without versions
    cli_runner.invoke(delete.version_cmd, ["-b", case_id], obj=populated_context, input="Yes")
    bundle_obj = store.get_bundle_by_name(bundle_name=case_id)
    assert len(bundle_obj.versions) == 0

    # WHEN trying to delete a bundle
    result = cli_runner.invoke(delete.bundle_cmd, [case_id], obj=populated_context, input="Yes")
    # THEN assert it exits non zero
    assert result.exit_code == 0
    # THEN it should communicate that it was deleted
    assert f"Deleted bundle {case_id}" in caplog.text
