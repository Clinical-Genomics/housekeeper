"""Tests for delete CLI functions"""

import logging
from pathlib import Path

from click.testing import CliRunner

from housekeeper.cli import delete
from housekeeper.store.models import Bundle, File
from housekeeper.store.store import Store


def test_delete_files_non_specified(base_context: dict, cli_runner: CliRunner, caplog):
    """Test to delete files without specifying bundle name or tag"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner

    # WHEN trying to delete files without specifying bundle name or tag
    result = cli_runner.invoke(delete.files_cmd, [], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1

    # THEN HAL9000 should interfere
    assert "Please specify" in caplog.text


def test_delete_files_non_existing_bundle(
    base_context: dict, cli_runner: CliRunner, case_id: str, caplog
):
    """Test to delete a non existing bundle"""
    caplog.set_level(logging.DEBUG)

    # GIVEN a context with a store and a cli runner

    # WHEN trying to delete a bundle which does not exist
    result = cli_runner.invoke(delete.files_cmd, ["--bundle-name", case_id], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1

    # THEN it should communicate that the bundle was not found
    assert f"Bundle {case_id} not found" in caplog.text


def test_delete_existing_bundle_with_confirmation(
    populated_context: dict, cli_runner: CliRunner, caplog
):
    """Test to delete an existing bundle with confirmation"""
    caplog.set_level(logging.DEBUG)

    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a existing bundle
    bundle: Bundle = store._get_query(table=Bundle).first()
    assert bundle
    case_id = bundle.name

    # WHEN trying to delete files without specifying bundle name or tag
    result = cli_runner.invoke(delete.files_cmd, ["--bundle-name", case_id], obj=populated_context)

    # THEN it should ask if you are sure
    assert "Are you sure you want to delete" in result.output


def test_delete_existing_bundle_no_confirmation(
    populated_context: dict, cli_runner: CliRunner, caplog
):
    """Test to delete an existing bundle without confirmation"""
    caplog.set_level(logging.DEBUG)

    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a existing bundle
    bundle: Bundle = store._get_query(table=Bundle).first()
    assert bundle

    case_id = bundle.name

    # GIVEN the bundle files
    files = store.get_files_before(bundle_name=case_id, tag_names=[])
    nr_files = len(files)
    assert nr_files > 0

    # WHEN trying to delete a bundle without requiring confirmation
    cli_runner.invoke(delete.files_cmd, ["--bundle-name", case_id, "--yes"], obj=populated_context)

    # THEN the bundle should have been removed
    assert "deleted" in caplog.text


def test_delete_file_skip_archived(
    populated_context: dict, cli_runner: CliRunner, spring_file_1: Path, caplog
):
    """Tests that an archived file is not deleted via the CLI."""
    caplog.set_level(logging.DEBUG)

    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a file with an archive entry
    file: File = store.get_files(file_path=spring_file_1.as_posix()).first()
    assert file.archive

    # WHEN trying to delete the file
    cli_runner.invoke(delete.file_cmd, ["--yes", str(file.id)], obj=populated_context)

    # THEN the file should not have been deleted
    assert "File is archived, please delete it with 'cg archive delete-file' instead" in caplog.text
    assert store.get_files(file_path=spring_file_1.as_posix()).first()


def test_delete_file(populated_context: dict, cli_runner: CliRunner, spring_file_2: Path, caplog):
    """Tests that a non-archived file is deleted via the CLI."""
    caplog.set_level(logging.DEBUG)

    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]

    # GIVEN a file with an archive entry
    file: File = store.get_files(file_path=spring_file_2.as_posix()).first()
    assert not file.archive

    # WHEN trying to delete the file
    cli_runner.invoke(delete.file_cmd, ["--yes", str(file.id)], obj=populated_context)

    # THEN the file should have been deleted
    assert not store.get_files(file_path=spring_file_2.as_posix()).first()
