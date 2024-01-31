"""Tests for adding tags via CLI"""

import logging

from housekeeper.cli.add import tag_cmd
from housekeeper.store.models import File
from housekeeper.store.store import Store


def test_add_tags_no_args(populated_context, cli_runner, caplog):
    """Test to add a two tags to the database"""
    # GIVEN a context with a populated store, and a cli runner
    caplog.set_level(logging.DEBUG)
    # GIVEN that there is no tag input
    # WHEN trying to add two tags to the an existing file
    result = cli_runner.invoke(tag_cmd, [], obj=populated_context)
    # THEN assert it has a zero exit status
    assert result.exit_code == 1
    # THEN check that the correct information is logged
    assert "No tags provided" in caplog.text


def test_add_two_tags(populated_context, cli_runner, caplog):
    """Test to add a two tags to the database"""
    # GIVEN a context with a populated store, and a cli runner
    caplog.set_level(logging.DEBUG)
    # GIVEN two new tags
    tag1 = "new-tag"
    tag2 = "other-tag"

    # WHEN trying to add two tags to the an existing file
    result = cli_runner.invoke(tag_cmd, [tag1, tag2], obj=populated_context)

    # THEN assert it has a zero exit status
    assert result.exit_code == 0
    # THEN check that the tags are logged
    assert tag1 in caplog.text
    # THEN check that the tags are logged
    assert tag2 in caplog.text
    # THEN assert that the tags are added to the data base
    db_tags = set([tag.name for tag in populated_context["store"].get_tags()])
    assert db_tags.intersection(set([tag1, tag2]))


def test_add_existing_tag_existing_file(populated_context, cli_runner, caplog):
    """Test to add a existing tag to a file that exists"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store, and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a existing file id
    file_id = 1
    file_obj: File = store.get_file_by_id(file_id=file_id)
    # GIVEN that the new tag already exists for the file
    tag = file_obj.tags[0].name

    # WHEN trying to add the existing tag to the file
    result = cli_runner.invoke(tag_cmd, [tag, "-f", str(file_id)], obj=populated_context)
    # THEN assert it has a non zero exit status
    assert result.exit_code == 0
    # THEN check that it communicates that the tag existed
    assert f"{tag}: tag already added" in caplog.text


def test_add_tag_existing_file(populated_context, cli_runner, caplog):
    """Test to add a non existing tag to a file that exists"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store, and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a existing file id
    file_id = 1
    file_obj: File = store.get_file_by_id(file_id=file_id)
    assert file_obj
    # GIVEN a new tag
    tag = "new-tag"

    # WHEN trying to add a tag to the existing file
    result = cli_runner.invoke(tag_cmd, [tag, "-f", str(file_id)], obj=populated_context)
    # THEN assert it has a zero exit status
    assert result.exit_code == 0
    # THEN check that the tag is displayed in the output
    assert f"{tag}: tag created" in caplog.text


def test_add_tag_non_existing_file(populated_context, cli_runner, caplog):
    """Test to add a tag to a file that not exist"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    store: Store = populated_context["store"]
    # GIVEN a non existing file id
    missing_file_id = 42
    file_obj = store.get_file_by_id(file_id=missing_file_id)
    assert not file_obj

    # WHEN trying to add a tag to the non existing file
    result = cli_runner.invoke(
        tag_cmd, ["new-tag", "-f", str(missing_file_id)], obj=populated_context
    )
    # THEN assert it has a non zero exit status
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert "unable to find file" in caplog.text
