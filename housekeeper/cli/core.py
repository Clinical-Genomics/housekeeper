# -*- coding: utf-8 -*-
import datetime

import click
import coloredlogs
import ruamel.yaml

import housekeeper
from housekeeper.exc import VersionIncludedError
from housekeeper.include import include_version
from housekeeper.store import Store


@click.group()
@click.option('-c', '--config', type=click.File())
@click.option('-d', '--database', help='path/URI of the SQL database')
@click.option('-l', '--log-level', default='INFO')
@click.version_option(housekeeper.__version__, prog_name=housekeeper.__title__)
@click.pass_context
def base(context, config, database, log_level):
    """Housekeeper - Access your files!"""
    coloredlogs.install(level=log_level)
    context.obj = ruamel.yaml.safe_load(config) if config else {}
    if database:
        context.obj['database'] = database


@base.command()
@click.option('--reset', is_flag=True, help='reset database before setting up tables')
@click.option('--force', is_flag=True, help='bypass manual confirmations')
@click.pass_context
def init(context, reset, force):
    """Setup the database."""
    store = Store(context.obj['database'])
    existing_tables = store.engine.table_names()
    if force or reset:
        if existing_tables and not force:
            message = f"Delete existing tables? [{', '.join(existing_tables)}]"
            click.confirm(click.style(message, fg='yellow'), abort=True)
        store.drop_all()
    elif existing_tables:
        click.echo(click.style("Database already exists, use '--reset'", fg='red'))
        context.abort()

    store.create_all()
    message = f"Success! New tables: {', '.join(store.engine.table_names())}"
    click.echo(click.style(message, fg='green'))


@base.command()
@click.option('-v', '--version', type=int, help='version id of the bundle version')
@click.argument('bundle_name', required=False)
@click.pass_context
def include(context, bundle_name, version):
    """Include a bundle of files into the internal space.

    Use bundle name if you simply want to inlcude the latest version.
    """
    store = Store(context.obj['database'])
    if version:
        version_obj = store.Version.get(version)
        if version_obj is None:
            click.echo(click.style('version not found', fg='red'))
    else:
        bundle_obj = store.bundle(bundle_name)
        if bundle_obj is None:
            click.echo(click.style('bundle not found', fg='red'))
        version_obj = bundle_obj.versions[0]

    try:
        include_version(context.obj['root'], version_obj)
    except VersionIncludedError as error:
        click.echo(click.style(error.message, fg='red'))
        context.abort()

    version_obj.included_at = datetime.datetime.now()
    store.commit()
    click.echo(click.style('included all files!', fg='green'))
