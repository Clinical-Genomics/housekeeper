"""Tests for adding bundles via CLI"""
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
    assert "bundle name already exists" in caplog.text


def test_add_bundle(base_context, cli_runner, case_id, caplog):
    """Test to add a new bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store and a cli runner
    bundle_name = case_id

    # WHEN trying to add a bundle
    result = cli_runner.invoke(bundle_cmd, [bundle_name], obj=base_context)

    # THEN assert it succeded
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert "new bundle added" in caplog.text
