"""Tests for delete CLI functions"""
import logging

from click import Context
from click.testing import CliRunner

from housekeeper.cli import delete
from housekeeper.store.api.core import Store


def test_delete_non_existing_tag(
    non_existent_tag_name: str,
    base_context: Context,
    cli_runner: CliRunner,
    caplog,
):
    """."""
    # GIVEN a tag that does not exist

    # WHEN trying to delete the non-existent tag
    result = cli_runner.invoke(delete.tag_cmd, ["--name", non_existent_tag_name], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the tag was not found
    assert f"Tag {non_existent_tag_name} not found" in caplog.text


def test_delete_tag():
    """."""
    # GIVEN

    # WHEN

    # THEN
