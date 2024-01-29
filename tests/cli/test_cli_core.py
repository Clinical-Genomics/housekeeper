"""Tests for the core cli"""

import logging

import housekeeper
from housekeeper.cli.core import base
from housekeeper.cli.init import init as init_command


def test_cli_title(cli_runner):
    """Test that the title is shown in output when running the version option"""
    # GIVEN a cli runner

    # WHEN asking to see the version
    result = cli_runner.invoke(base, ["--version"])

    # THEN it should display the title of the program
    assert housekeeper.__title__ in result.output


def test_cli_version(cli_runner):
    """Test that the version is shown in output when running the version option"""
    # GIVEN a cli runner
    # WHEN asking to see the version
    result = cli_runner.invoke(base, ["--version"])
    # THEN it should display the version of the program
    assert housekeeper.__version__ in result.output


def test_init_config(config_file, cli_runner):
    """Test init housekeeper with a config file"""
    # GIVEN a config file and a cli runner

    # WHEN calling the CLI
    result = cli_runner.invoke(base, ["--config", str(config_file), "init"])

    # THEN it should read the config and import it to the context
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_init_database(db_uri, db_path, cli_runner, project_dir):
    """Test init housekeeper with cli options"""
    # GIVEN a uri, a non existing database, a project dir and a cli runner
    assert not db_path.exists()

    # WHEN calling the CLI
    result = cli_runner.invoke(base, ["--database", db_uri, "--root", project_dir, "init"])

    # THEN the database should have been created
    assert db_path.exists()
    # THEN success should be communicated
    assert "Success!" in result.output


def test_init_database_no_specified_database(cli_runner):
    """Test init housekeeper without specifying a database"""
    # GIVEN a cli runner

    # WHEN running the init command without any database or project dir
    result = cli_runner.invoke(base, ["init"])

    # THEN command should exit with a one as exit status
    assert result.exit_code == 1
    # THEN it should be communicated that there is no database
    assert "Please point to a database" in result.output


def test_init_database_no_specified_root_dir(cli_runner, db_uri):
    """Test init housekeeper without specifying a root dir"""
    # GIVEN a cli runner

    # WHEN running the init command without any database or project dir
    result = cli_runner.invoke(base, ["--database", db_uri, "init"])

    # THEN command should exit with a one as exit status
    assert result.exit_code == 1
    # THEN it should be communicated that there is no root dir
    assert "Please specify a root dir" in result.output


def test_init_existing_database(cli_runner, base_context, db_path, caplog):
    """Test to initialise a housekeeper instance when db already exists"""
    caplog.set_level(logging.INFO)
    # GIVEN the uri to an initialised database, a project dir and a cli runner
    assert db_path.exists()

    # WHEN trying to intitialize existing db
    result = cli_runner.invoke(init_command, [], obj=base_context)

    # THEN a controlled exit should be made
    assert result.exit_code == 1
    # THEN it should communicate that the database exists
    assert "Database already exists" in caplog.text


def test_override_existing_database(cli_runner, db_path, base_context, caplog):
    """Test init housekeeper database and overwrite existing one"""
    caplog.set_level(logging.INFO)
    # GIVEN the uri to an initialised database, a project dir and a cli runner
    assert db_path.exists()

    # WHEN intitializing and overriding existing db
    result = cli_runner.invoke(init_command, ["--reset"], obj=base_context, input="Yes")

    # THEN it should communicate that the database exists
    assert "Delete existing tables?" in result.output
    # THEN it should communicate success
    assert "Success!" in caplog.text


def test_force_override_existing_database(cli_runner, db_path, base_context, caplog):
    """Test init housekeeper database and overwrite existing one"""
    caplog.set_level(logging.INFO)
    # GIVEN the uri to an initialised database, a project dir and a cli runner
    assert db_path.exists()

    # WHEN intitializing and overriding existing db
    cli_runner.invoke(init_command, ["--force"], obj=base_context)

    # THEN it should communicate success
    assert "Success!" in caplog.text
