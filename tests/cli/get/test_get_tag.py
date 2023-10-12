"""Tests for the get tags cli functionality."""

import logging

from click import Context
from click.testing import CliRunner, Result
from sqlalchemy.orm import Query

from housekeeper.cli.add import tag_cmd as add_tags
from housekeeper.cli.get import tag_cmd


def test_get_tags_empty(cli_runner: Context, base_context: CliRunner, caplog):
    """Test to get tags from an empty database"""
    caplog.set_level(logging.DEBUG)
    # GIVEN an empty database, log_output and a cli runner

    # WHEN getting all tags
    res: Result = cli_runner.invoke(tag_cmd, obj=base_context)

    # THEN assert it exits without problems
    assert res.exit_code == 0
    # THEN assert it communicates that the tags where not found
    assert "Could not find any of the specified tags" in caplog.text


def test_get_tags(cli_runner: Context, base_context: CliRunner, caplog):
    """Test to get tags from a database with some tags"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a database with some tags
    tag_names: list[str] = ["tag1", "tag2", "tag3"]
    cli_runner.invoke(add_tags, tag_names, obj=base_context)
    tag_query: Query = base_context["store"].get_tags()
    assert tag_query

    # WHEN getting all tags
    res: Result = cli_runner.invoke(tag_cmd, obj=base_context)

    # THEN assert it exits without problems
    assert res.exit_code == 0
    assert tag_names[0] in caplog.text


def test_get_tags_non_existing(
    cli_runner: Context, base_context: CliRunner, non_existent_tag_name, caplog
):
    """Test to get a non-existing tag from a database with some tags"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a database with some tags
    tag_names: list[str] = ["tag1", "tag2", "tag3"]
    cli_runner.invoke(add_tags, tag_names, obj=base_context)

    # WHEN getting tag that does not exist
    other_tag: str = non_existent_tag_name
    res: Result = cli_runner.invoke(tag_cmd, ["-n", other_tag], obj=base_context)

    # THEN assert it exits without problems
    assert res.exit_code == 0
    assert "Could not find any of the specified tags" in caplog.text


def test_get_tags_json(cli_runner: Context, base_context: CliRunner, caplog):
    """Test to get tags from a database with some tags in json format"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a database with some tags
    tag_names: list[str] = ["tag1", "tag2", "tag3"]
    cli_runner.invoke(add_tags, tag_names, obj=base_context)
    tag_query: Query = base_context["store"].get_tags()
    assert tag_query

    # WHEN getting all tags
    res: Result = cli_runner.invoke(tag_cmd, ["--json"], obj=base_context)

    # THEN assert it exits without problems
    assert res.exit_code == 0
