"""Tests for CLI delete functions"""

from housekeeper.cli import delete

# delete file


def test_delete_non_existing_file(base_context, cli_runner):
    """Test to delete a non existing file"""
    # GIVEN a context with a store, a file id and a cli runner
    file_id = 1
    # GIVEN that the file does not exist
    store = base_context["store"]
    file_obj = store.File.get(file_id)
    assert not file_obj

    # WHEN trying to delete the non existing file
    result = cli_runner.invoke(delete.file_cmd, [str(file_id)], obj=base_context)
    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the file was not found
    assert "file not found" in result.output


def test_delete_existing_file_with_confirmation(populated_context, cli_runner):
    """Test to delete an existing file using confirmation"""
    # GIVEN a context with a populated store, a file id and a cli runner
    store = populated_context["store"]
    file_id = 1
    # GIVEN that the file exists
    file_obj = store.File.get(file_id)
    assert file_obj
    # WHEN trying to delete the file
    result = cli_runner.invoke(delete.file_cmd, [str(file_id)], obj=populated_context)
    # THEN it should ask if you are sure
    assert "remove file from" in result.output


def test_delete_existing_file_no_confirmation(populated_context, cli_runner):
    """Test to delete a existing file without confirmation"""
    # GIVEN a context with a populated store, a file id and a cli runner
    store = populated_context["store"]
    file_id = 1
    # GIVEN that the file exists
    file_obj = store.File.get(file_id)
    assert file_obj
    # WHEN trying to delete the file
    result = cli_runner.invoke(
        delete.file_cmd, [str(file_id), "--yes"], obj=populated_context
    )
    # THEN file delete should be in output
    assert "file deleted" in result.output


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


def test_delete_existing_bundle_with_confirmation(
    populated_context, cli_runner, case_id
):
    """Test to delete an existing bundle"""
    # GIVEN a context with a store and a cli runner
    # WHEN trying to delete a bundle
    result = cli_runner.invoke(delete.bundle, [case_id], obj=populated_context)
    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should ask if you are sure
    assert "remove bundle version from" in result.output


def test_delete_existing_bundle_no_confirmation(populated_context, cli_runner, case_id):
    """Test to delete an existing bundle without confirmation"""
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
    """Test to delete files without specifying bundle name or tag"""
    # GIVEN a context with a store and a cli runner
    # WHEN trying to delete files without specifying bundle name or tag
    result = cli_runner.invoke(delete.files, [], obj=base_context)
    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN HAL9000 should interfere
    assert "Please specify a bundle or a tag" in result.output


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


def test_delete_existing_bundle_with_confirmation(
    populated_context, cli_runner, case_id
):
    """Test to delete an existing bundle with confirmation"""
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


def test_delete_existing_bundle_no_confirmation(populated_context, cli_runner, case_id):
    """Test to delete an existing bundle without confirmation"""
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
    result = cli_runner.invoke(
        delete.files, ["--bundle-name", case_id, "--yes"], obj=populated_context
    )
    # THEN the bundle should have been removed
    assert "deleted" in result.output
