"""Tests foe adding files via CLI"""

import logging
from pathlib import Path

from click import Context
from click.testing import CliRunner

from housekeeper.cli.add import file_cmd
from housekeeper.store.models import Bundle, Version
from housekeeper.store.store import Store

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


def test_add_new_file_existing_bundle_with_include(
    populated_context: dict,
    cli_runner: CliRunner,
    case_id: str,
    second_sample_vcf: Path,
    caplog,
    housekeeper_version_dir: Path,
    project_dir: Path,
):
    """Test to add a new file to an existing bundle"""
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

    # THEN assert it succeeds
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert NEW_FILE_ADDED in caplog.text
    # THEN check that the file has been included in the version and that the relative path is given
    assert Path(housekeeper_version_dir, second_sample_vcf.name).exists()
    assert Path(housekeeper_version_dir, second_sample_vcf.name).is_file()
    assert Path(version_obj.files[2].path) == Path(
        version_obj.relative_root_dir, second_sample_vcf.name
    )


def test_add_new_file_existing_bundle_without_include(
    populated_context: Context,
    cli_runner: CliRunner,
    case_id: str,
    second_sample_vcf: Path,
    caplog,
    housekeeper_version_dir: Path,
):
    """Test to add a file to an existing bundle"""
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


def test_add_file_when_different_file_with_same_name_exists_in_bundle_directory(
    populated_context: dict,
    cli_runner: CliRunner,
    case_id: str,
    second_sample_vcf: Path,
    housekeeper_version_dir: Path,
    caplog,
):
    """Test adding a file to an existing bundle when a different file with the same name already exists in the bundle directory."""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    bundle_name = case_id

    store: Store = populated_context["store"]
    bundle_obj: Bundle = store.bundles().first()
    version_obj: Version = bundle_obj.versions[0]

    # GIVEN that there is a file in the bundle directory
    file_in_housekeeper_bundle: Path = Path(housekeeper_version_dir, second_sample_vcf.name)
    open(file_in_housekeeper_bundle, "w").close()

    # WHEN trying to add a file with the same name to the bundle
    result = cli_runner.invoke(
        file_cmd,
        [str(second_sample_vcf), "-b", bundle_name],
        obj=populated_context,
    )

    # THEN assert it fails
    assert result.exit_code == 1
    # THEN check that an error message is displayed
    assert "linked file:" not in caplog.text
    # THEN check that the file was not added to the housekeeper bundle version
    housekeeper_files: list[Path] = [Path(file.path) for file in version_obj.files]
    assert file_in_housekeeper_bundle not in housekeeper_files


def test_add_file_in_bundle_directory(
    populated_context: dict,
    cli_runner: CliRunner,
    case_id: str,
    housekeeper_version_dir: Path,
    caplog,
):
    """Test adding a file to an existing bundle given that the file is in the bundle directory."""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    bundle_name = case_id

    store: Store = populated_context["store"]
    bundle_obj: Bundle = store.bundles().first()
    version_obj: Version = bundle_obj.versions[0]

    # GIVEN that the file is in the bundle directory
    file_name: str = "file_in_housekeeper_bundle.txt"
    file_in_housekeeper_bundle: Path = Path(housekeeper_version_dir, file_name)
    open(file_in_housekeeper_bundle, "w").close()

    # WHEN trying to add a file with the same name to the bundle
    result = cli_runner.invoke(
        file_cmd,
        [str(file_in_housekeeper_bundle), "-b", bundle_name],
        obj=populated_context,
    )

    # THEN assert it succeeds
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert NEW_FILE_ADDED in caplog.text
    # THEN check that the file was added to the housekeeper bundle version
    housekeeper_files: list[Path] = [Path(file.path) for file in version_obj.files]
    assert Path(version_obj.relative_root_dir, file_name) in housekeeper_files


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
