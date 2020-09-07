"""Tests foe adding files via CLI"""
import logging
from pathlib import Path

from click import Context
from click.testing import CliRunner

from housekeeper.cli.add import file_cmd


def test_add_file_non_existing_bundle(
    base_context: Context,
    cli_runner: CliRunner,
    case_id: str,
    second_sample_vcf: Path,
    caplog,
):
    """Test to add a file to a non existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store and a cli runner
    unknown_bundle_name = case_id

    # WHEN trying to add a bundle
    result = cli_runner.invoke(
        file_cmd, [str(second_sample_vcf), "-b", unknown_bundle_name], obj=base_context
    )

    # THEN assert it fails
    assert result.exit_code == 1
    # THEN check that the proper information is displayed
    assert f"unknown bundle: {unknown_bundle_name}" in caplog.text


def test_add_file_no_input(base_context: Context, cli_runner: CliRunner, caplog):
    """Test to add a file without specifying any input"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store and a cli runner

    # WHEN trying to add a bundle
    result = cli_runner.invoke(file_cmd, [], obj=base_context)

    # THEN assert it fails since there is no valid input
    assert result.exit_code == 1
    # THEN check that the proper information is displayed
    assert "Please input json or path" in caplog.text


def test_add_file_existing_bundle(
    populated_context: CliRunner,
    cli_runner: CliRunner,
    case_id: str,
    second_sample_vcf: Path,
    caplog,
):
    """Test to add a file to a existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    bundle_name = case_id

    # WHEN trying to add the file to a bundle
    result = cli_runner.invoke(
        file_cmd, [str(second_sample_vcf), "-b", bundle_name], obj=populated_context
    )

    # THEN assert it succedes
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert "new file added" in caplog.text
