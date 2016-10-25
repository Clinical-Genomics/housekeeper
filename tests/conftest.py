# -*- coding: utf-8 -*-
from functools import partial

from alchy import Manager
from click.testing import CliRunner
from path import Path
import pytest
import yaml

from housekeeper.cli import root
from housekeeper.store import api, Model
from housekeeper.pipelines.mip.parse import prepare_inputs


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, root)


@pytest.fixture
def pedigree():
    return dict(
        checksum='13c366da11437d46e66dfe33cd8cb884d9c1488e',
        path='tests/fixtures/mip/cust003/16074/genomes/16074/16074_pedigree.txt'
    )


@pytest.yield_fixture(scope='function')
def mip_output():
    mip_out = Path('tests/fixtures/mip')
    yield mip_out
    mod_qcmetrics = mip_out.joinpath("cust003/16074/analysis/genomes/16074/"
                                     "16074_qcmetrics.mod.yaml")
    mod_qcmetrics.remove_p()
    meta_suffix = "cust003/16074/analysis/genomes/meta.yaml"
    new_meta = mip_out.joinpath(meta_suffix)
    new_meta.remove_p()


@pytest.yield_fixture(scope='function')
def manager():
    config = dict(SQLALCHEMY_DATABASE_URI='sqlite://')
    _manager = Manager(config=config, Model=Model)
    _manager.create_all()
    yield _manager
    _manager.drop_all()


@pytest.yield_fixture(scope='function')
def setup_tmp(tmpdir):
    tmp_path = Path(tmpdir).joinpath('analyses')
    tmp_path.makedirs_p()
    db_path = tmp_path.joinpath('store.sqlite3')
    uri = "sqlite:///{}".format(db_path)
    manager = api.manager(uri)
    manager.create_all()
    data = dict(uri=uri, root=tmp_path, path=str(db_path), manager=manager)
    yield data
    manager.drop_all()


@pytest.fixture()
def config_path(mip_output):
    suffix = "cust003/16074/genomes/16074/16074_config.yaml"
    _config_path = mip_output.joinpath(suffix)
    return _config_path


@pytest.fixture()
def config_data(config_path):
    with open(config_path, "r") as in_handle:
        _config_data = yaml.load(in_handle)
    return _config_data


@pytest.fixture()
def segments(config_data):
    _segments = prepare_inputs(config_data)
    return _segments
