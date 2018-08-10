from pathlib import Path
import shutil

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
    """Delete all versions of a bundle."""
    bundle_obj = context.obj['store'].bundle(bundle_name)
    if bundle_obj is None:
        click.echo(click.style('bundle not found', fg='red'))
        context.abort()

    versions_obj = bundle_obj.versions
    creation_dates = [version.created_at.strftime('%Y-%m-%d') for version in versions_obj]
    if len(creation_dates) > 1:
        echo_dates = ", ".join(creation_dates[:-1]) + " and " + creation_dates[-1]
    else:
        echo_dates = creation_dates[0]

    question = f"Remove all versions from bundle {bundle_name} with the following creation " \
               f"date(s): {echo_dates}?"
    if yes or click.confirm(click.style(question, fg='yellow')):
        # delete bundle and all versions fomr disk
        shutil.rmtree(bundle_obj.full_path, ignore_errors=True)
        # delete all files belonging to bundle from housekeeper
        files_query = context.obj['store'].files(bundle=bundle_obj.name)
        for file_obj in files_query:
            file_obj.delete()
        # delete all versions in bundle from housekeeper
        for version_obj in versions_obj:
            click.echo(click.style(f"version deleted: "
                                   f"{version_obj.created_at.strftime('%Y-%m-%d')} of bundle "
                                   f"{bundle_obj.name}", fg='green'))
            version_obj.delete()
            #  TODO: error message when not commiting right after deleting version from database.
            #  Check cascading in Model!
            context.obj['store'].commit()
        # delete bundle from housekeeper
        bundle_obj.delete()
        context.obj['store'].commit()

    # version_obj = bundle_obj.versions[0]
    # if version_obj.included_at:
    #     question = f"remove bundle version from file system and database: {version_obj.full_path}"
    # else:
    #     question = f"remove bundle version from database: {version_obj.created_at.date()}"


@delete.command()
@click.option('--yes', multiple=True, is_flag=True, help='skip checks')
@click.option('-t', '--tag', multiple=True, help='file tag')
@click.option('-b', '--bundle', help='bundle name')
@click.option('-a', '--before', help='version created before...')
@click.option('-n', '--notondisk', is_flag=True, help='rm db entry from files not on disk')
@click.pass_context
def files(context, yes, tag, bundle, before, notondisk):
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

    query = context.obj['store'].files_before(bundle = bundle, tags = tag, before = before)

    if notondisk:
        file_objs = set(query) - context.obj['store'].files_ondisk(query)
    else:
        file_objs = query.all()

    if len(file_objs) > 0 and len(yes) < 2:
        if not click.confirm(f"Are you sure you want to delete {len(file_objs)} files?"):
            context.abort()

    for file_obj in file_objs:
        if yes or click.confirm(f"remove file from disk and database: {file_obj.full_path}"):
            file_obj_path = Path(file_obj.full_path)
            if file_obj.is_included and (file_obj_path.exists() or file_obj_path.is_symlink()):
                file_obj_path.unlink()
            file_obj.delete()
            context.obj['store'].commit()
            click.echo(f'{file_obj.full_path} deleted')


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
