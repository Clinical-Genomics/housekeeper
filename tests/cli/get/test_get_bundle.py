"""Tests for adding via CLI"""

from housekeeper.cli.get import get


def test_get_existing_bundle(populated_context, cli_runner):
    """Test to get the files from a bundle that exists"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    bundle_name = bundle_obj.name

    # WHEN trying to add a bundle that exists
    result = cli_runner.invoke(get, [bundle_name], obj=populated_context)

    # THEN assert it has a non zero exit status
    assert result.exit_code == 0


def test_get_existing_bundle_verbose(populated_context, cli_runner):
    """Test to get verbose output files from a bundle that exists"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    bundle_name = bundle_obj.name

    # WHEN trying to add a bundle that exists
    result = cli_runner.invoke(get, [bundle_name, "--verbose"], obj=populated_context)

    # THEN assert it has a non zero exit status
    assert result.exit_code == 0
