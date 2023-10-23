"""Tests for delete CLI functions"""

import logging
from pathlib import Path

from click import Context
from click.testing import CliRunner

from housekeeper.cli import delete
from housekeeper.include import include_version
from housekeeper.store.api.core import Store
from housekeeper.store.models import File


def test_delete_non_existing_file(base_context: Context, cli_runner: CliRunner, caplog):
    """Test to delete a non existing file"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store, a file id and a cli runner
    file_id = 1
    # GIVEN that the file does not exist
    store = base_context["store"]
    file_obj: File = store.get_file_by_id(file_id=file_id)
    assert not file_obj

    # WHEN trying to delete the non existing file
    result = cli_runner.invoke(delete.file_cmd, [str(file_id)], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the file was not found
    assert "file not found" in caplog.text


def test_delete_existing_file_with_confirmation(
    populated_context: Context, cli_runner: CliRunner, caplog
):
    """Test to delete an existing file using confirmation"""
    # GIVEN a context with a populated store, a file id and a cli runner
    store: Store = populated_context["store"]
    file_id = 1
    # GIVEN that the file exists
    file_obj: File = store.get_file_by_id(file_id=file_id)
    assert file_obj

    # WHEN trying to delete the file
    result = cli_runner.invoke(delete.file_cmd, [str(file_id)], obj=populated_context)

    # THEN it should ask if you are sure
    assert "remove file from" in result.output


def test_delete_existing_file_no_confirmation(
    populated_context: Context, cli_runner: CliRunner, caplog
):
    """Test to delete a existing file without confirmation"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store, a file id and a cli runner
    store: Store = populated_context["store"]
    file_id = 1
    # GIVEN that the file exists
    file_obj: File = store.get_file_by_id(file_id=file_id)
    assert file_obj

    # WHEN trying to delete the file
    result = cli_runner.invoke(delete.file_cmd, [str(file_id), "--yes"], obj=populated_context)

    # THEN file delete should be in output
    assert "file deleted" in caplog.text


def test_delete_sample_sheet(
    populated_context: Context, cli_runner: CliRunner, caplog, flow_cell_id: str, sample_sheet: Path
):
    # GIVEN a bundle with a file tagged with sample-sheet
    store: Store = populated_context["store"]
    assert store.get_files(file_path=str(sample_sheet)).one()

    # WHEN deleting the sample sheet
    cli_runner.invoke(
        delete.delete_sample_sheet, [str(flow_cell_id), "--yes"], obj=populated_context
    )

    # THEN the sample sheet should be deleted
    assert not store.get_files(file_path=str(sample_sheet)).first()


def test_delete_sample_sheet_included(
    populated_context: Context, cli_runner: CliRunner, caplog, flow_cell_id: str, sample_sheet: Path
):
    # GIVEN an included bundle with a file tagged with sample-sheet
    store: Store = populated_context["store"]
    sample_sheet_file: File = store.get_files(file_path=str(sample_sheet)).one()
    include_version(global_root=populated_context["root"], version_obj=sample_sheet_file.version)
    assert sample_sheet_file
    assert sample_sheet_file.is_included
    assert Path(sample_sheet_file.full_path).exists()

    # WHEN deleting the sample sheet
    cli_runner.invoke(
        delete.delete_sample_sheet,
        [flow_cell_id, "--yes"],
        obj=populated_context,
    )

    # THEN the sample sheet should be deleted from the database
    assert not store.get_files(file_path=str(sample_sheet)).first()

    # THEN the included sample sheet should also be deleted from disk
    assert not Path(sample_sheet_file.full_path).exists()
