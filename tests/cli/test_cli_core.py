# -*- coding: utf-8 -*-
from pathlib import Path

import ruamel.yaml

import housekeeper
from housekeeper.store import Store


def test_cli_version(invoke_cli):
    # GIVEN I want to see the version of the program
    # WHEN asking to see the version
    result = invoke_cli(['--version'])
    # THEN it should display the version of the program
    # THEN it should print the name and version of the tool only
    assert housekeeper.__title__ in result.output
    assert housekeeper.__version__ in result.output


def test_cli_config(tmpdir, invoke_cli):
    # GIVEN a simple, valid cli
    config_file = tmpdir.join('config.yaml')
    config_file.write(ruamel.yaml.safe_dump(dict(root=str(tmpdir), database='sqlite://')))
    # WHEN calling the CLI
    result = invoke_cli(['--config', str(config_file), 'init', '--help'])
    # THEN it should read the config and import it to the context
    assert result.exit_code == 0
    # ... not sure how to test :-( ...


def test_cli_init(cli_runner, invoke_cli):
    # GIVEN you want to setup a new database using the CLI
    database = './test_db.sqlite3'
    database_path = Path(database)
    database_uri = f"sqlite:///{database}"
    with cli_runner.isolated_filesystem():
        assert database_path.exists() is False

        # WHEN calling "init"
        result = invoke_cli(['--database', database_uri, '--root', '.', 'init'])

        # THEN it should setup the database with some tables
        assert result.exit_code == 0
        assert database_path.exists()
        assert len(Store(database_uri, root='/tmp').engine.table_names()) > 0

        # GIVEN the database already exists
        # WHEN calling the init function
        result = invoke_cli(['--database', database_uri, '--root', '.', 'init'])
        # THEN it should print an error and give error exit code
        assert result.exit_code != 0
        assert 'Database already exists' in result.output

        # GIVEN the database already exists
        # WHEN calling "init" with "--reset"
        result = invoke_cli(['--database', database_uri, '--root', '.', 'init', '--reset'],
                            input='Yes')
        # THEN it should re-setup the tables and print new tables
        assert result.exit_code == 0
        assert 'Success!' in result.output
