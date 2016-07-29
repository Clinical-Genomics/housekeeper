# -*- coding: utf-8 -*-
from path import path

from housekeeper import initiate


def test_setup(tmpdir):
    # GIVEN an empty directory
    root_dir = tmpdir.join('keeper')
    root_path = path(root_dir)
    assert not root_path.exists()
    # WHEN setting up a new housekeeper system
    initiate.setup(root_path)
    # THEN the directory should be filled with stuff
    assert root_path.exists()
    assert root_path.joinpath('store.sqlite3').isfile()
    assert root_path.joinpath('analyses').isdir()
    assert root_path.joinpath('housekeeper.yaml').isfile()


def test_init(invoke_cli, tmpdir):
    # GIVEN a non-existing directory
    root_path = tmpdir.join('keeper')
    assert not path(root_path).exists()
    # WHEN executing the init command
    result = invoke_cli(['init', str(root_path)])
    # THEN it should return successfully
    assert result.exit_code == 0


def test_init_existing(invoke_cli, tmpdir):
    # GIVEN an existing directory
    assert path(tmpdir).exists()
    # WHEN running the init command
    result = invoke_cli(['init', str(tmpdir)])
    # THEN it should exit unsuccesfully
    assert result.exit_code != 0
