from pathlib import Path
import shutil
from dateutil.parser import parse as parse_date

import click

from housekeeper.store import Store, models


@click.group()
@click.pass_context
def delete(context):
    """Delete things in the database."""
    context.obj['store'] = Store(context.obj['database'], context.obj['root'])


@delete.command()
@click.option('-y', '--yes', is_flag=True, help='skip checks')
@click.argument('bundle_name')
@click.pass_context
def bundle(context, yes, bundle_name):
    """Delete the latest bundle version."""
    bundle_obj = context.obj['store'].bundle(bundle_name)
    if bundle_obj is None:
        click.echo(click.style('bundle not found', fg='red'))
        context.abort()
    version_obj = bundle_obj.versions[0]
    if version_obj.included_at:
        question = f"remove bundle version from file system and database: {version_obj.root_dir}"
    else:
        question = f"remove bundle version from database: {version_obj.created_at.date()}"
    if yes or click.confirm(question):
        if version_obj.included_at:
            shutil.rmtree(version_obj.root_dir, ignore_errors=True)
        version_obj.delete()
        context.obj['store'].commit()
        click.echo(f"version deleted: {version_obj.root_dir}")


@delete.command()
@click.option('-y', '--yes', is_flag=True, help='skip checks')
@click.option('-t', '--tag', multiple=True, help='file tag')
@click.option('-b', '--bundle', help='bundle name')
@click.option('-a', '--before', help='version created before...')
@click.option('-u', '--unassociated', is_flag=True, help='rm db entry from files not on disk')
@click.pass_context
def files(context, yes, tag, bundle, before, unassociated):
    """Delete files based on tags."""
    file_objs = []

    if not tag and not bundle:
        click.echo("I'm afraid I can't let you do that.")
        context.abort()

    if bundle:
        bundle_obj = context.obj['store'].bundle(bundle)
        if bundle_obj is None:
            click.echo(click.style('bundle not found', fg='red'))
            context.abort()

    query = context.obj['store'].files(tags=tag, bundle=bundle)
    if before:
        before_dt = parse_date(before)
        query = query.join(models.Version).filter(models.Version.created_at < before_dt)
    import ipdb; ipdb.set_trace()
    file_objs = query.all()

    if unassociated:
        for i, file_obj in reversed(list(enumerate(file_objs))):
            file_path = Path(file_obj.full_path)
            if file_path.is_file():
                del file_objs[i]

    for file_obj in file_objs:
        if yes or click.confirm(f"remove file from disk and database: {file_obj.full_path}"):
            if file_obj.is_included and Path(file_obj.full_path).exists():
                Path(file_obj.full_path).unlink()

        file_obj.delete()
        context.obj['store'].commit()
        click.echo('{file_obj.full_path} deleted')


@delete.command('file')
@click.option('-y', '--yes', is_flag=True, help='skip checks')
@click.argument('file_id', type=int)
@click.pass_context
def file_cmd(context, yes, file_id):
    """Delete a file."""
    file_obj = context.obj['store'].File.get(file_id)
    if file_obj.is_included:
        question = f"remove file from file system and database: {file_obj.full_path}"
    else:
        question = f"remove file from database: {file_obj.full_path}"
    if yes or click.confirm(question):
        if file_obj.is_included and Path(file_obj.full_path).exists():
            Path(file_obj.full_path).unlink()

        file_obj.delete()
        context.obj['store'].commit()
        click.echo('file deleted')
