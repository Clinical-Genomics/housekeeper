"""Module for base CLI"""
import click
import coloredlogs
import ruamel.yaml

import housekeeper
from housekeeper.store import Store

from . import add, delete, get, include, init


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
    context.obj["database"] = database if database else context.obj["database"]
    context.obj["root"] = root if root else context.obj["root"]
    context.obj["store"] = Store(context.obj["database"], context.obj["root"])


base.add_command(init.init)
base.add_command(add.add)
base.add_command(include.include)
base.add_command(get.get)
base.add_command(delete.delete)
