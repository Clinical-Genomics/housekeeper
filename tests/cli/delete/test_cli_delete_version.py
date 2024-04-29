"""Tests for delete version CLI functions"""

import logging

from click import Context
from click.testing import CliRunner

from housekeeper.cli import delete


def test_delete_non_version_no_input(base_context: Context, cli_runner: CliRunner, caplog):
    """Test to delete a version without any input

    The command should fail since there is no input
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a store and a cli runner

    # WHEN trying to delete a version without specifying anything
    result = cli_runner.invoke(delete.version_cmd, [], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the bundle was not found
    assert "Please select a bundle or a version" in caplog.text
