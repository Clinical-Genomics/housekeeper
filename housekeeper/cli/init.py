"""Initialise HK db from CLI"""
import logging
import click
from housekeeper.store.api.core import Store
from sqlalchemy import inspect


LOG = logging.getLogger(__name__)


@click.command()
@click.option("--reset", is_flag=True, help="reset database before setting up tables")
@click.option("--force", is_flag=True, help="bypass manual confirmations")
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    store: Store = context.obj["store"]
    inspector = inspect(store.engine)
    existing_tables = inspector.get_table_names()

    if force or reset:
        if existing_tables and not force:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg="yellow"), abort=True)
        store.drop_all()
    elif existing_tables:
        LOG.error("Database already exists, use '--reset'")
        context.abort()

    store.create_all()
    LOG.info(f"Success! New tables: {', '.join(inspector.get_table_names())}")
