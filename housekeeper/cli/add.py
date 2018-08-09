# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List

import click
import datetime as dt

from housekeeper.store import Store


@click.group()
@click.pass_context
def add(context):
    """Add things to the store."""
    context.obj['db'] = Store(context.obj['database'], context.obj['root'])


@add.command()
@click.argument('name')
@click.argument('new-version', 'new_version', is_flag=true)
@click.pass_context
def bundle(context, name, new_version):
    """Add a new bundle."""
    cur_bundle = context.obj['db'].bundle(name)
    if not new_version and cur_bundle:
        click.echo(click.style('bundle name already exists', fg='yellow'))
        context.abort()

    if not new_version:
        new_bundle = context.obj['db'].new_bundle(name)
        context.obj['db'].add_commit(new_bundle)
        created_at = new_bundle.created_at
    else:
        created_at = dt.datetime.now()

    # add default version
    new_version = context.obj['db'].new_version(created_at=created_at)
    new_version.bundle = cur_bundle if cur_bundle else new_bundle
    context.obj['db'].add_commit(new_version)

    if new_version:
        click.echo(click.style(f"new version added: {cur_bundle.name} ({new_version.created_at})", fg='green'))
    else:
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


@add.command()
@click.argument('file_id', type=int)
@click.argument('tags', nargs=-1)
@click.pass_context
def tag(context: click.Context, file_id: int, tags: List[str]):
    """Add tags to an existing file."""
    file_obj = context.obj['db'].file_(file_id)
    if file_obj is None:
        print(click.style('unable to find file', fg='red'))
        context.abort()
    for tag_name in tags:
        tag_obj = context.obj['db'].tag(tag_name)
        if tag_obj is None:
            tag_obj = context.obj['db'].new_tag(tag_name)
        elif tag_obj in file_obj.tags:
            print(click.style(f"{tag_name}: tag already added", fg='yellow'))
            continue
        file_obj.tags.append(tag_obj)
    context.obj['db'].commit()
    all_tags = (tag.name for tag in file_obj.tags)
    print(click.style(f"file tags: {', '.join(all_tags)}", fg='blue'))
