# -*- coding: utf-8 -*-
import logging

import click
from path import path

from housekeeper.store import api, Metadata

log = logging.getLogger(__name__)


def setup_db(root_path, db_uri, reset=False):
    """Setup database with tables and store config.

    Args:
        root_path (path): root to store analyses
        db_uri (str): connection string to database
        reset (Optional[bool]): whether to reset an existing database
    """
    log.info("setup a new database: %s", db_uri)
    db = api.manager(db_uri)
    if reset:
        db.drop_all()
    db.create_all()

    log.debug('add metadata about the system')
    meta = Metadata(root=root_path)
    db.add_commit(meta)


@click.command()
@click.option('--db-only', is_flag=True)
@click.option('--reset', is_flag=True)
@click.argument('root', type=click.Path())
@click.pass_context
def init(context, db_only, reset, root):
    """Setup the housekeeper."""
    root_path = path(root).abspath()
    if not db_only:
        if root_path.exists():
            log.error("root path already exists: %s", root_path)
            context.abort()
        else:
            log.info("create root folder to store analyses: %s", root)
            path(root).makedirs_p()
    uri = context.obj.get('database')
    db_uri = uri or "sqlite:///{}".format(root_path.joinpath('store.sqlite3'))
    setup_db(root_path, db_uri=db_uri, reset=reset)
