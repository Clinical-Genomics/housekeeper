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


def test_cli_delete_files(tmpdir, invoke_cli, bundle_data):
    config_file = tmpdir.join('config.yaml')
    database_path = Path(tmpdir).joinpath('database.sqlite')
    config_file.write(ruamel.yaml.safe_dump(dict(root=str(tmpdir), database='sqlite:///' + str(database_path))))
    store = Store(uri='sqlite:///' + str(database_path), root=str(tmpdir))
    store.create_all()

    # GIVEN you want to remove everything
    result = invoke_cli(['--config', str(config_file), 'delete', 'files'])
    # THEN HAL9000 should interfere
    assert result.exit_code == 1
    assert result.output == "I'm afraid I can't let you do that.\nAborted!\n"

    # GIVEN you want to delete a not existing bundle
    result = invoke_cli(['--config', str(config_file),'delete', 'files', '--bundle', 'sillyfish'])
    # THEN it should not be found
    assert result.exit_code == 1
    assert result.output == "bundle not found\nAborted!\n"

    # GIVEN you want to delete a bundle
    bundle_obj, version_obj = store.add_bundle(data=bundle_data)
    store.add_commit(bundle_obj)
    result = invoke_cli(['--config', str(config_file),'delete', 'files', '--bundle', 'sillyfish'])
    # THEN it should ask you if you are sure
    assert result.exit_code == 1
    assert result.output == "Are you sure you want to delete 2 files? [y/N]: \nAborted!\n"

    store.drop_all()
