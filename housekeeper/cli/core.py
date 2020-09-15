"""Module for base CLI"""
import logging

import click
import coloredlogs
import ruamel.yaml

import housekeeper
from housekeeper.store import Store

from . import add, delete, get, include, init

LOG = logging.getLogger(__name__)


@click.group()
@click.option("-c", "--config", type=click.File())
@click.option("-d", "--database", help="path/URI of the SQL database")
@click.option("-r", "--root", type=click.Path(exists=True), help="Housekeeper root dir")
@click.option("-l", "--log-level", default="INFO")
@click.version_option(housekeeper.__version__, prog_name=housekeeper.__title__)
@click.pass_context
def base(context, config, database, root, log_level):
    """Housekeeper - Access your files!"""
    coloredlogs.install(level=log_level)
    context.obj = ruamel.yaml.safe_load(config) if config else {}
    db_path = database if database else context.obj.get("database")
    root_path = context.obj["root"] = root if root else context.obj.get("root")
    if not db_path:
        LOG.error("Please point to a database")
        raise click.Abort
    if not root_path:
        LOG.error("Please specify a root dir")
        raise click.Abort
    LOG.info("Use database %s", db_path)
    context.obj["database"] = db_path
    LOG.info("Use root path %s", root_path)
    context.obj["store"] = Store(db_path, root_path)


base.add_command(init.init)
base.add_command(add.add)
base.add_command(include.include)
base.add_command(get.get)
base.add_command(delete.delete)
