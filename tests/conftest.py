# -*- coding: utf-8 -*-
from functools import partial

from alchy import Manager
from click.testing import CliRunner
import pytest

from housekeeper.cli import root
from housekeeper.store.models import Model


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, root)


@pytest.yield_fixture(scope='function')
def manager():
    config = dict(SQLALCHEMY_DATABASE_URI='sqlite://')
    _manager = Manager(config=config, Model=Model)
    _manager.create_all()
    yield _manager
    _manager.drop_all()


@pytest.yield_fixture(scope='function')
def manager_tmp(tmpdir):
    db_path = tmpdir.join('temp.sqlite3')
    uri = "sqlite:///{}".format(db_path)
    config = dict(SQLALCHEMY_DATABASE_URI=uri)
    manager = Manager(config=config, Model=Model)
    data = dict(uri=uri, path=str(db_path), manager=manager)
    yield data
    manager.drop_all()
