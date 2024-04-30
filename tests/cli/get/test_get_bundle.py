"""Tests for adding via CLI"""

from housekeeper.cli.get import bundle_cmd
from housekeeper.store.models import Bundle
from housekeeper.store.store import Store


def test_get_existing_bundle_name(populated_context, cli_runner, helpers):
    """Test to fetch an existing bundle based on name"""

    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a existing bundle
    bundle: Bundle = store._get_query(table=Bundle).first()
    assert bundle

    bundle_name = bundle.name

    # WHEN trying to fetch the bundle based on bundle name
    output = helpers.get_stdout(
        cli_runner.invoke(bundle_cmd, [bundle_name], obj=populated_context).output
    )

    # THEN assert that the bundle was written to terminal
    assert bundle_name in output


def test_get_existing_bundle_verbose(populated_context, cli_runner, helpers):
    """Test to fetch an existing bundle based on name."""

    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a existing bundle
    bundle: Bundle = store._get_query(table=Bundle).first()
    assert bundle
    bundle_name = bundle.name

    # WHEN trying to fetch the bundle based on bundle name
    output = helpers.get_stdout(
        cli_runner.invoke(bundle_cmd, [bundle_name], obj=populated_context).output
    )
    # THEN assert that the files are printed
    assert "files" in output


def test_get_non_existing_bundle_name(base_context, cli_runner, helpers, case_id):
    """Test to fetch a non existing bundle based on name when store is empty"""

    # GIVEN a context with a empty store and a cli runner
    store = base_context["store"]

    # GIVEN that there are no bundles
    assert helpers.count_iterable(store.bundles()) == 0

    # WHEN trying to fetch the bundle based on bundle name
    output = helpers.get_stdout(cli_runner.invoke(bundle_cmd, [case_id], obj=base_context).output)

    # THEN assert that no bundle was written to terminal
    assert case_id not in output


def test_get_non_existing_bundle_populated_store(
    populated_context, cli_runner, other_case_id, helpers
):
    """Test to fetch a non existing bundle based on name when bundles exists"""
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a non empty store
    assert helpers.count_iterable(store.bundles()) > 0

    # GIVEN a bundle name that does not exist in database
    assert store.get_bundle_by_name(bundle_name=other_case_id) is None

    # WHEN trying to fetch the non existing bundle
    output = helpers.get_stdout(
        cli_runner.invoke(bundle_cmd, [other_case_id], obj=populated_context).output
    )

    # THEN assert that no bundle was written to terminal
    assert other_case_id not in output


def test_get_existing_bundle_id(populated_context, cli_runner, helpers):
    """Test to fetch an existing bundle based on bundle id"""
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a existing bundle
    bundle = store._get_query(table=Bundle).first()
    bundle_id = bundle.id

    # WHEN trying to fetch a bundle based on bundle id
    json_bundles = helpers.get_json(
        cli_runner.invoke(bundle_cmd, ["-i", bundle_id, "--json"], obj=populated_context).output
    )

    # THEN assert that the bundle was printed to screen
    assert isinstance(json_bundles, list)
    assert len(json_bundles) == 1


def test_get_bundle_json(populated_context, cli_runner, helpers):
    """Test to fetch a bundle in json format"""

    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a existing bundle
    bundle = store._get_query(table=Bundle).first()
    bundle_id = bundle.id

    # WHEN fetching the bundle in json format
    json_bundles = helpers.get_json(
        cli_runner.invoke(bundle_cmd, ["-i", bundle_id, "--json"], obj=populated_context).output
    )

    # THEN assert that the output is a list of bundles
    assert isinstance(json_bundles, list)

    # THEN assert that the bundles are dictionaries
    assert isinstance(json_bundles[0], dict)


def test_get_bundles_multiple_bundles(populated_context, cli_runner, helpers, other_bundle):
    """Test to get all bundles when there are more than one bundle"""

    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    helpers.add_bundle(store, other_bundle)

    # GIVEN a store with more than one bundles
    nr_bundles = helpers.count_iterable(store.bundles())
    assert nr_bundles > 1

    # WHEN fetching all bundles by not specifying any bundle
    json_bundles = helpers.get_json(
        cli_runner.invoke(bundle_cmd, ["--json"], obj=populated_context).output
    )

    # THEN assert that all bundles where fetched
    assert len(json_bundles) == nr_bundles


def test_get_bundles_no_bundle(base_context, cli_runner, helpers):
    """Test to get all bundles when there are no bundles"""

    # GIVEN a context with a populated store and a cli runner
    store = base_context["store"]

    # GIVEN a store without bundles
    assert helpers.count_iterable(store.bundles()) == 0

    # WHEN fetching all bundles by not specifying any bundle
    json_bundles = helpers.get_json(
        cli_runner.invoke(bundle_cmd, ["--json"], obj=base_context).output
    )

    # THEN assert that we still get a list
    assert isinstance(json_bundles, list)

    # THEN assert that no bundles where fetched
    assert len(json_bundles) == 0
