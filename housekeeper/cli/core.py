"""Module for base CLI"""

import logging

import click
import coloredlogs
import yaml

import housekeeper
from housekeeper.constants import ROOT
from housekeeper.services.file_service.file_service import FileService
from housekeeper.services.file_report_service.file_report_service import FileReportService
from housekeeper.store.database import initialize_database
from housekeeper.store.store import Store

from . import add, delete, get, include, init

LOG = logging.getLogger(__name__)


@click.group()
@click.option("-c", "--config", type=click.File())
@click.option("-d", "--database", help="path/URI of the SQL database")
@click.option("-r", "--root", type=click.Path(exists=True), help="Housekeeper root dir")
@click.option("-l", "--log-level", default="INFO")
@click.version_option(housekeeper.__version__, prog_name=housekeeper.__title__)
@click.pass_context
def base(
    context: click.Context,
    config: click.File,
    database: str | None,
    root: str | None,
    log_level: str,
):
    """Housekeeper - Access your files!"""
    coloredlogs.install(level=log_level)
    config_values = {}
    if config:
        config_values = yaml.full_load(config)
    context.obj = config_values
    db_path = database or context.obj.get("database")
    root_path = context.obj[ROOT] = root or context.obj.get(ROOT)
    if not db_path:
        LOG.error("Please point to a database")
        raise click.Abort
    if not root_path:
        LOG.error("Please specify a root dir")
        raise click.Abort
    context.obj["database"] = db_path
    LOG.info("Use root path %s", root_path)
    initialize_database(db_path)
    store = Store(root=root_path)
    context.obj["store"] = store
    context.obj["file_service"] = FileService(store)
    context.obj["file_report_service"] = FileReportService()


base.add_command(init.init)
base.add_command(add.add)
base.add_command(include.include)
base.add_command(get.get)
base.add_command(delete.delete)
