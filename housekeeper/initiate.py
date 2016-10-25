# -*- coding: utf-8 -*-
import logging

import click
from path import Path

from housekeeper.store import api

log = logging.getLogger(__name__)


def setup_db(db_uri, reset=False):
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


@click.command()
@click.option('--db-only', is_flag=True)
@click.option('--reset', is_flag=True)
@click.argument('root', type=click.Path())
@click.pass_context
def init(context, db_only, reset, root):
    """Setup the housekeeper."""
    root_path = Path(root).abspath()
    if not db_only:
        if root_path.exists():
            log.error("root path already exists: %s", root_path)
            context.abort()
        else:
            log.info("create root folder to store analyses: %s", root)
            root_path.makedirs_p()
    uri = context.obj.get('database')
    db_uri = uri or "sqlite:///{}".format(root_path.joinpath('store.sqlite3'))
    setup_db(db_uri, reset=reset)
