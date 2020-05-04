"""Tests for CLI delete functions"""

from housekeeper.cli import delete

# delete bundle


def test_delete_non_existing_bundle(base_context, cli_runner, case_id):
    """Test to delete a non existing bundle"""
    # GIVEN a context with a store and a cli runner
    # WHEN trying to delete a bundle
    result = cli_runner.invoke(delete.bundle, [case_id], obj=base_context)
    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the bundle was not found
    assert "bundle not found" in result.output


def test_delete_existing_bundle_no_input(populated_context, cli_runner, case_id):
    """Test to delete a non existing bundle"""
    # GIVEN a context with a store and a cli runner
    # WHEN trying to delete a bundle
    result = cli_runner.invoke(delete.bundle, [case_id], obj=populated_context)
    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should ask if you are sure
    assert "remove bundle version from" in result.output


def test_delete_existing_bundle(populated_context, cli_runner, case_id):
    """Test to delete a non existing bundle"""
    # GIVEN a context with a store and a cli runner
    # WHEN trying to delete a bundle
    result = cli_runner.invoke(
        delete.bundle, [case_id], obj=populated_context, input="Yes"
    )
    # THEN assert it exits non zero
    assert result.exit_code == 0
    # THEN it should communicate that it was deleted
    assert "version deleted:" in result.output


# delete files


def test_delete_files_non_specified(base_context, cli_runner):
    """Test to delete files"""
    # GIVEN a context with a store and a cli runner
    # WHEN trying to delete files without specifying bundle name or tag
    result = cli_runner.invoke(delete.files, [], obj=base_context)
    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN HAL9000 should interfere
    assert "I'm afraid I can't let you do that" in result.output


def test_delete_files_non_existing_bundle(base_context, cli_runner, case_id):
    """Test to delete a non existing bundle"""
    # GIVEN a context with a store and a cli runner
    # WHEN trying to delete a bundle
    result = cli_runner.invoke(
        delete.files, ["--bundle-name", case_id], obj=base_context
    )
    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the bundle was not found
    assert "bundle not found" in result.output


def test_delete_files_existing_bundle_no_input(populated_context, cli_runner, case_id):
    """Test to delete a non existing bundle"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    case_id = bundle_obj.name

    # WHEN trying to delete files without specifying bundle name or tag
    result = cli_runner.invoke(
        delete.files, ["--bundle-name", case_id], obj=populated_context
    )
    # THEN it should ask if you are sure
    assert "Are you sure you want to delete" in result.output


def test_delete_files_existing_bundle(populated_context, cli_runner, case_id):
    """Test to delete a non existing bundle"""
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

    # WHEN trying to delete files without specifying bundle name or tag
    result = cli_runner.invoke(
        delete.files, ["--bundle-name", case_id], obj=populated_context, input="Yes"
    )
    # THEN the files should have been removed
    assert "remove file from disk and database" in result.output
