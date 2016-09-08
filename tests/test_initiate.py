    # -*- coding: utf-8 -*-
from path import path

from housekeeper import initiate


def test_init(invoke_cli, tmpdir):
    # GIVEN a non-existing directory
    root_path = tmpdir.join('keeper')
    db_path = tmpdir.join('store.sqlite3')
    db_uri = path("sqlite:///{}".format(str(db_path)))
    assert not path(root_path).exists()
    # WHEN executing the init command
    result = invoke_cli(['--database', db_uri, 'init', str(root_path)])
    # THEN it should return successfully
    assert path(root_path).exists()
    assert result.exit_code == 0


def test_init_existing(invoke_cli, tmpdir):
    # GIVEN an existing directory
    db_path = tmpdir.join('store.sqlite3')
    db_uri = path("sqlite:///{}".format(str(db_path)))
    assert path(tmpdir).exists()
    assert not db_path.exists()
    # WHEN running the init command
    result = invoke_cli(['--database', db_uri, 'init', str(tmpdir)])
    # THEN it should exit unsuccesfully
    assert result.exit_code != 0
    assert not db_path.exists()
