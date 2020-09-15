"""Tests for delete CLI functions"""

import logging
from click import Context
from click.testing import CliRunner

from housekeeper.cli import delete


def test_delete_files_non_specified(base_context: Context, cli_runner: CliRunner, caplog):
    """Test to delete files without specifying bundle name or tag"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner

    # WHEN trying to delete files without specifying bundle name or tag
    result = cli_runner.invoke(delete.files_cmd, [], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN HAL9000 should interfere
    assert "Please specify a bundle or a tag" in caplog.text


def test_delete_files_non_existing_bundle(
    base_context: Context, cli_runner: CliRunner, case_id: str, caplog
):
    """Test to delete a non existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner

    # WHEN trying to delete a bundle
    result = cli_runner.invoke(delete.files_cmd, ["--bundle-name", case_id], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the bundle was not found
    assert "Bundle not found" in caplog.text


def test_delete_existing_bundle_with_confirmation(
    populated_context: Context, cli_runner: CliRunner, case_id: str, caplog
):
    """Test to delete an existing bundle with confirmation"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    case_id = bundle_obj.name

    # WHEN trying to delete files without specifying bundle name or tag
    result = cli_runner.invoke(delete.files_cmd, ["--bundle-name", case_id], obj=populated_context)
    # THEN it should ask if you are sure
    assert "Are you sure you want to delete" in result.output


def test_delete_existing_bundle_no_confirmation(
    populated_context: Context, cli_runner: CliRunner, case_id: str, caplog
):
    """Test to delete an existing bundle without confirmation"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    case_id = bundle_obj.name
    # GIVEN the bundle files
    query = store.files_before(bundle=case_id, tags=())
    nr_files = query.count()
    assert nr_files > 0

    # WHEN trying to delete a bundle without requiring confirmation
    cli_runner.invoke(delete.files_cmd, ["--bundle-name", case_id, "--yes"], obj=populated_context)
    # THEN the bundle should have been removed
    assert "deleted" in caplog.text
