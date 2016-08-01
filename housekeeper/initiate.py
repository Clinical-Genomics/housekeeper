# -*- coding: utf-8 -*-
import logging

import click
from path import path
import yaml

from housekeeper.store import get_manager, Metadata

log = logging.getLogger(__name__)


def setup(root_path, uri=None):
    """Setup a new structure and database."""
    log.info("create the root directory: %s", root_path)
    abs_root = path(root_path).abspath()
    abs_root.joinpath('analyses').makedirs_p()

    db_uri = uri or "sqlite:///{}".format(abs_root.joinpath('store.sqlite3'))
    log.info("setup a new database: %s", db_uri)
    db = get_manager(db_uri)
    db.create_all()

    log.debug('add metadata about the system')
    meta = Metadata(root=abs_root)
    db.add_commit(meta)

    config = abs_root.joinpath('housekeeper.yaml')
    log.info("generate a config file: %s", config)
    data = dict(database=db_uri, root=str(abs_root))
    with config.open('w') as stream:
        dump = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        stream.write(dump.decode('utf-8'))


@click.command()
@click.argument('root', type=click.Path())
@click.pass_context
def init(context, root):
    """Setup the housekeeper."""
    if path(root).exists():
        log.error("root folder already exists: %s", root)
        context.abort()
    else:
        setup(root, uri=context.obj.get('database'))
