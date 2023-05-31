"""Tests foe adding files via CLI"""
import logging
from pathlib import Path

from click import Context
from click.testing import CliRunner
from housekeeper.cli.add import file_cmd
from housekeeper.store import Store
from housekeeper.store.models import Bundle, Version

NEW_FILE_ADDED: str = "new file added"


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


def test_add_file_json_and_file_path(
    base_context: Context,
    cli_runner: CliRunner,
    file_data_json: str,
    sample_vcf: Path,
    caplog,
):
    """Test to add a file to a non existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store and a cli runner

    # WHEN trying to add a bundle
    result = cli_runner.invoke(
        file_cmd, [str(sample_vcf), "--json", file_data_json], obj=base_context
    )

    # THEN assert it fails
    assert result.exit_code == 1
    # THEN check that the proper information is displayed
    assert "Can not input both json and path" in caplog.text


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


def test_add_non_existing_file(base_context: Context, cli_runner: CliRunner, caplog):
    """Test to add a file without specifying any input"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store and a cli runner
    non_existing = Path("hello.txt")
    assert not non_existing.exists()

    # WHEN trying to add a bundle
    result = cli_runner.invoke(file_cmd, [str(non_existing)], obj=base_context)

    # THEN assert it fails since there is no valid input
    assert result.exit_code == 1
    # THEN check that the proper information is displayed
    assert f"File: {non_existing} does not exist" in caplog.text


def test_add_file_existing_bundle_with_include(
    populated_context: dict,
    cli_runner: CliRunner,
    case_id: str,
    second_sample_vcf: Path,
    caplog,
    housekeeper_version_dir: Path,
    project_dir: Path,
):
    """Test to add a file to a existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    bundle_name = case_id

    store: Store = populated_context["store"]
    bundle_obj: Bundle = store.bundles().first()
    version_obj: Version = bundle_obj.versions[0]

    # WHEN trying to add the file to a bundle
    result = cli_runner.invoke(
        file_cmd,
        [str(second_sample_vcf), "-b", bundle_name],
        obj=populated_context,
    )

    # THEN assert it succedes
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert NEW_FILE_ADDED in caplog.text
    # THEN check that the file has been included in the version and that the relative path is given
    assert Path(housekeeper_version_dir, second_sample_vcf.name).exists()
    assert Path(housekeeper_version_dir, second_sample_vcf.name).is_file()
    assert Path(version_obj.files[2].path) == Path(
        version_obj.relative_root_dir, second_sample_vcf.name
    )


def test_add_file_existing_bundle_without_include(
    populated_context: Context,
    cli_runner: CliRunner,
    case_id: str,
    second_sample_vcf: Path,
    caplog,
    housekeeper_version_dir: Path,
):
    """Test to add a file to a existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    bundle_name = case_id

    # WHEN trying to add the file to a bundle
    result = cli_runner.invoke(
        file_cmd,
        [str(second_sample_vcf), "-b", bundle_name, "-kip"],
        obj=populated_context,
    )

    # THEN assert the program exits with success
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert NEW_FILE_ADDED in caplog.text


def test_add_file_json(
    populated_context: Context,
    cli_runner: CliRunner,
    file_data_json: str,
    housekeeper_version_dir: Path,
    caplog,
):
    """Test to add a file in json format to a non existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a populated store and a cli runner

    # WHEN trying to add a bundle
    result = cli_runner.invoke(file_cmd, ["--json", file_data_json], obj=populated_context)

    # THEN assert it fails
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert NEW_FILE_ADDED in caplog.text
