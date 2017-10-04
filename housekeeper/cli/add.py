# -*- coding: utf-8 -*-
from pathlib import Path

import click

from housekeeper.store import Store


@click.group()
@click.pass_context
def add(context):
    """Add things to the store."""
    context.obj['db'] = Store(context.obj['database'], context.obj['root'])


@add.command()
@click.argument('name')
@click.pass_context
def bundle(context, name):
    """Add a new bundle."""
    if context.obj['db'].bundle(name):
        click.echo(click.style('bundle name already exists', fg='yellow'))
        context.abort()
    new_bundle = context.obj['db'].new_bundle(name)
    context.obj['db'].add_commit(new_bundle)

    # add default version
    new_version = context.obj['db'].new_version(created_at=new_bundle.created_at)
    new_version.bundle = new_bundle
    context.obj['db'].add_commit(new_version)

    click.echo(click.style(f"new bundle added: {new_bundle.name} ({new_bundle.id})", fg='green'))


@add.command('file')
@click.option('-t', '--tag', 'tags', multiple=True, help='tag to associate the file by')
@click.option('-a', '--archive', is_flag=True, help='mark file to be archived')
@click.argument('bundle_name')
@click.argument('path')
@click.pass_context
def file_cmd(context, tags, archive, bundle_name, path):
    """Add a file to a bundle."""
    bundle_obj = context.obj['db'].bundle(bundle_name)
    if bundle_obj is None:
        click.echo(click.style(f"unknown bundle: {bundle_name}", fg='red'))
        context.abort()
    version_obj = bundle_obj.versions[0]
    new_file = context.obj['db'].new_file(
        path=str(Path(path).absolute()),
        to_archive=archive,
        tags=[context.obj['db'].tag(tag_name) if context.obj['db'].tag(tag_name) else
              context.obj['db'].new_tag(tag_name) for tag_name in tags]
    )
    new_file.version = version_obj
    context.obj['db'].add_commit(new_file)
    click.echo(click.style(f"new file added: {new_file.path} ({new_file.id})", fg='green'))
