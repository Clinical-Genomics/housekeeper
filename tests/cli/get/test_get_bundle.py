"""Tests for adding via CLI"""

from housekeeper.cli.get import bundle_cmd


def test_get_existing_bundle_name(populated_context, cli_runner):
    """Test to fetch an existing bundle based on name"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    bundle_name = bundle_obj.name

    # WHEN trying to fetch the bundle based on bundle name
    result = cli_runner.invoke(bundle_cmd, ["-n", bundle_name], obj=populated_context)

    # THEN assert that the bundle was written to terminal
    assert bundle_name in result.output


def test_get_existing_bundle_id(populated_context, cli_runner):
    """Test to fetch an existing bundle based on bundle id"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    bundle_id = bundle_obj.id

    # WHEN trying to fetch a bundle based on bundle id
    result = cli_runner.invoke(bundle_cmd, ["-i", bundle_id], obj=populated_context)

    # THEN assert that the bundle was printed to screen
    assert bundle_obj.name in result.output


def test_get_bundle_json(populated_context, cli_runner, helpers):
    """Test to fetch a bundle in json format"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    bundle_id = bundle_obj.id

    # WHEN fetching the bundle in json format
    result = cli_runner.invoke(
        bundle_cmd, ["-i", bundle_id, "--json"], obj=populated_context
    )
    json_bundles = helpers.get_json(result.output)

    # THEN assert that the output is a list of bundles
    assert isinstance(json_bundles, list)
    # THEN assert that the bundles are dictionaries
    assert isinstance(json_bundles[0], dict)


def test_get_bundles_multiple_bundles(
    populated_context, cli_runner, helpers, other_bundle
):
    """Test to get all bundles when there are more than one bundle"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    helpers.add_bundle(store, other_bundle)
    # GIVEN a store with more than one bundles
    nr_bundles = helpers.count_iterable(store.bundles())
    assert nr_bundles > 1

    # WHEN fetching all bundles by not specifying any bundle
    result = cli_runner.invoke(bundle_cmd, ["--json"], obj=populated_context)
    json_bundles = helpers.get_json(result.output)

    # THEN assert that all bundles where fetched
    assert len(json_bundles) == nr_bundles
