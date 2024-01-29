"""Initialise HK db from CLI"""

import logging

import click

from housekeeper.store.database import create_all_tables, drop_all_tables, get_tables

LOG = logging.getLogger(__name__)


@click.command()
@click.option("--reset", is_flag=True, help="reset database before setting up tables")
@click.option("--force", is_flag=True, help="bypass manual confirmations")
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    existing_tables: list[str] = get_tables()

    if force or reset:
        if existing_tables and not force:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg="yellow"), abort=True)
        drop_all_tables()
    elif existing_tables:
        LOG.error("Database already exists, use '--reset'")
        context.abort()

    create_all_tables()
    LOG.info(f"Success! New tables: {', '.join(get_tables())}")
