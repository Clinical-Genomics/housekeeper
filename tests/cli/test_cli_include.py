"""Tests for include cli command"""
import logging
from datetime import datetime
from click import Context
from click.testing import CliRunner

from housekeeper.cli.include import include
from housekeeper.cli.add import bundle_cmd


def test_include_files_creates_bundle_dir(populated_context: Context, cli_runner: CliRunner):
    """Test to include the files of a version for a bundle_name

    The bundle should not exist before and after command is run it should have been created
    """
    # GIVEN a context that is populated
    store = populated_context["store"]
    bundle_obj = store.Bundle.query.first()
    bundle_name = bundle_obj.name
    # GIVEN that the latest version of the bundle is not included
    assert bundle_obj.versions[0].included_at is None
    # GIVEN that no folder has been created since case is not included
    bundle_path = populated_context["root"] / bundle_obj.name
    assert not bundle_path.exists()

    # WHEN running the include files command
    result = cli_runner.invoke(include, [bundle_name], obj=populated_context)

    # THEN assert that the bundle path was created
    assert bundle_path.exists()


def test_include_files_creates_version_specific_bundle_dir(
    populated_context: Context, cli_runner: CliRunner
):
    """Test to include the files of a version for a bundle_name

    The version bundle should not exist before and after command is run it should have been created
    """
    # GIVEN a context that is populated
    store = populated_context["store"]
    bundle_obj = store.Bundle.query.first()
    version_obj = bundle_obj.versions[0]
    bundle_name = bundle_obj.name
    # GIVEN that the latest version of the bundle is not included
    assert version_obj.included_at is None
    # GIVEN that no version specific folder has been created since version is not included
    version_path = populated_context["root"] / bundle_obj.name / str(version_obj.created_at.date())
    assert not version_path.exists()

    # WHEN running the include files command
    result = cli_runner.invoke(include, [bundle_name], obj=populated_context)

    # THEN assert that the version path was created
    assert version_path.exists()


def test_include_files_adds_version_specific_files(
    populated_context: Context, cli_runner: CliRunner
):
    """Test to include the files of a version for a bundle_name

    The files should have been hard linked after command has been run
    """
    # GIVEN a context that is populated
    store = populated_context["store"]
    bundle_obj = store.Bundle.query.first()
    version_obj = bundle_obj.versions[0]
    bundle_name = bundle_obj.name
    # GIVEN that the latest version of the bundle is not included
    assert version_obj.included_at is None
    # GIVEN that no version specific folder has been created since version is not included
    version_path = populated_context["root"] / bundle_obj.name / str(version_obj.created_at.date())
    assert not version_path.exists()

    # WHEN running the include files command
    result = cli_runner.invoke(include, [bundle_name], obj=populated_context)

    # THEN assert that files are included in the folder
    files_included = []
    for file_path in version_path.iterdir():
        files_included.append(file_path)

    assert files_included
    assert len(files_included) == len(version_obj.files)


def test_include_files_specific_version(populated_context: Context, cli_runner: CliRunner):
    """Test to include the files of a version by specifying the version id

    The folder should have been created
    """
    # GIVEN a context that is populated
    store = populated_context["store"]
    bundle_obj = store.Bundle.query.first()
    version_obj = bundle_obj.versions[0]
    version_id = version_obj.id
    # GIVEN that the latest version of the bundle is not included
    assert version_obj.included_at is None
    # GIVEN that no version specific folder has been created since version is not included
    version_path = populated_context["root"] / bundle_obj.name / str(version_obj.created_at.date())
    assert not version_path.exists()

    # WHEN running the include files command
    result = cli_runner.invoke(include, ["--version-id", version_id], obj=populated_context)

    # THEN assert that the folder was created
    assert version_path.exists()

    # THEN assert that files are included in the folder
    files_included = []
    for file_path in version_path.iterdir():
        files_included.append(file_path)

    assert files_included
    assert len(files_included) == len(version_obj.files)


def test_include_version_no_args(populated_context: Context, cli_runner: CliRunner, caplog):
    """Test to include the files of a version without specifying bundle name or version

    The command should exit since it needs to be specified
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context that is populated

    # WHEN running the include files command without args
    result = cli_runner.invoke(include, [], obj=populated_context)

    # THEN assert that the command exists with zero code 1
    assert result.exit_code == 1
    # THEN assert it was communicated that arguments are needed
    assert "use bundle name or version-id" in caplog.text


def test_include_non_existing_version(populated_context: Context, cli_runner: CliRunner, caplog):
    """Test to include the files of a version that does not exist

    The command should exit since a valid version is needed
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context that is populated
    store = populated_context["store"]
    # GIVEN a version that does not exists
    version_id = 10
    assert not store.Version.get(version_id)

    # WHEN running the include files specifying the non existing version
    result = cli_runner.invoke(include, ["--version-id", version_id], obj=populated_context)

    # THEN assert that the command exists with zero code 1
    assert result.exit_code == 1
    # THEN assert it was communicated that version did not exist
    assert "version not found" in caplog.text


def test_include_non_existing_bundle(
    base_context: Context, cli_runner: CliRunner, timestamp: datetime, caplog
):
    """Test to include the files in the latest version of a bundle that does not exist

    The command should exit since a valid bundle is needed
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN context and a bundle_name that does not exist
    store = base_context["store"]
    bundle_name = "hello"
    assert not store.bundle(name=bundle_name)

    # WHEN running the include files specifying bundle without versions
    result = cli_runner.invoke(include, [bundle_name], obj=base_context)

    # THEN assert that the command exists with zero code 1
    assert result.exit_code == 1
    # THEN assert it was communicated that the bundle did not exist
    assert f"bundle {bundle_name} not found" in caplog.text


def test_include_bundle_without_version(
    base_context: Context, cli_runner: CliRunner, timestamp: datetime, caplog
):
    """Test to include the files in the latest version of a bundle that does not have versions

    The command should exit since a valid bundle with versions are needed
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN context with a bundle without versions
    store = base_context["store"]
    bundle_name = "hello"

    new_bundle = store.new_bundle(name=bundle_name, created_at=timestamp)
    store.add_commit(new_bundle)

    bundle_obj = store.bundle(name=bundle_name)
    assert len(bundle_obj.versions) == 0

    # WHEN running the include files specifying bundle without versions
    result = cli_runner.invoke(include, [bundle_name], obj=base_context)

    # THEN assert that the command exists with zero code 1
    assert result.exit_code == 1
    # THEN assert it was communicated that version did not exist
    assert f"Could not find any versions for bundle {bundle_name}" in caplog.text


def test_include_version_already_included(
    populated_context: Context, cli_runner: CliRunner, caplog
):
    """Test to include the files of a version that is already included

    The command should exit since the version can not be included again
    """
    caplog.set_level(logging.DEBUG)
    # GIVEN a context that is populated and a version that is already included
    store = populated_context["store"]
    version_obj = store.Version.query.first()
    version_id = version_obj.id
    result = cli_runner.invoke(include, ["--version-id", version_id], obj=populated_context)

    # WHEN trying to include the version again
    result = cli_runner.invoke(include, ["--version-id", version_id], obj=populated_context)

    # THEN assert that the command exists with zero code 1
    assert result.exit_code == 1
    # THEN assert it was communicated that version did not exist
    assert "version included on" in caplog.text
