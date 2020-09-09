"""Tests for include cli command"""

from click import Context
from click.testing import CliRunner

from housekeeper.cli.include import include


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

    The bundle should not exist before and after command is run it should have been created
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
