"""Tests for delete CLI functions"""

import logging

from click import Context
from click.testing import CliRunner

from housekeeper.cli import delete
from housekeeper.store.models import File, Tag
from housekeeper.store.store import Store


def test_delete_non_existing_tag(
    non_existent_tag_name: str,
    base_context: Context,
    cli_runner: CliRunner,
    caplog,
):
    """Test trying to delete a non-existent tag."""
    # GIVEN a tag that does not exist

    # WHEN trying to delete the non-existent tag
    result = cli_runner.invoke(delete.tag_cmd, ["--name", non_existent_tag_name], obj=base_context)

    # THEN assert it exits non zero
    assert result.exit_code == 1
    # THEN it should communicate that the tag was not found
    assert f"Tag {non_existent_tag_name} not found" in caplog.text


def test_delete_existing_tag_with_confirmation(
    populated_context: Context, cli_runner: CliRunner, caplog, family_tag_name: str
):
    """Test deleting an existing tag with confirmation."""
    # GIVEN an existing tag in a populated store
    store: Store = populated_context["store"]
    tag: Tag = store.get_tag(tag_name=family_tag_name)
    assert tag

    # WHEN trying to delete the tag
    result = cli_runner.invoke(delete.tag_cmd, ["--name", family_tag_name], obj=populated_context)

    # THEN the confirmation question should be shown in stdout
    assert f"Delete tag {family_tag_name} with" in result.output


def test_delete_existing_tag_no_confirmation(
    populated_context: Context, cli_runner: CliRunner, caplog, family_tag_name: str
):
    """Test deleting an existing tag without confirmation."""
    # GIVEN an existing tag in a populated store
    caplog.set_level(logging.DEBUG)
    store: Store = populated_context["store"]
    tag: Tag = store.get_tag(tag_name=family_tag_name)
    assert tag

    # WHEN trying to delete the tag
    result = cli_runner.invoke(
        delete.tag_cmd, ["--name", family_tag_name, "--yes"], obj=populated_context
    )

    # THEN the tag should have been deleted
    assert result.exit_code == 0
    assert f"Tag {family_tag_name} deleted" in caplog.text
    assert not store.get_tag(tag_name=family_tag_name)


def test_delete_tag_without_deleting_file(
    base_context: Context,
    populated_store: Store,
    cli_runner: CliRunner,
):
    """Test that deleting a tag does not delete files with the tag."""
    # GIVEN a file with a tag
    file_with_tag: File = populated_store.get_file_by_id(file_id=1)
    assert file_with_tag
    tag: Tag = file_with_tag.tags[0]
    assert tag

    # WHEN deleting the tag
    cli_runner.invoke(delete.tag_cmd, ["--name", tag.name, "--yes"], obj=base_context)

    # THEN the tag is deleted
    assert not populated_store.get_tag(tag_name=tag.name)
    # THEN the file is not deleted
    file_without_tag: File = populated_store.get_files(file_path=file_with_tag.path).first()
    assert file_without_tag
    # THEN the file no longer has the tag
    assert tag not in file_without_tag.tags
