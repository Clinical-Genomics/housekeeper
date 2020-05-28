"""Tests for the get tags cli functionality"""

from housekeeper.cli.get import tag_cmd


def test_get_tags_empty(cli_runner, base_context, log_output):
    """Test to get tags from a empty database"""
    # GIVEN a empty database, log_output and a cli runner

    # WHEN getting all tags
    res = cli_runner.invoke(tag_cmd, obj=base_context)

    # THEN assert it exits without problems
    assert res.exit_code == 0
    # THEN assert it communicates that the tags where not found
    assert "Could not find any of the specified tags" in log_output.text
