from pathlib import Path

import click

from housekeeper.store import Store


@click.group()
@click.pass_context
def delete(context):
    """Delete things in the database."""
    context.obj['store'] = Store(context.obj['database'], context.obj['root'])


@delete.command('file')
@click.option('-y', '--yes', is_flag=True, help='skip checks')
@click.argument('file_id', type=int)
@click.pass_context
def file_cmd(context, yes, file_id):
    """Delete a file."""
    file_obj = context.obj['store'].File.get(file_id)
    if yes or click.confirm(f"remove file: {file_obj.full_path}?"):
        if file_obj.is_included and file_obj.full_path.exists():
            file_obj.full_path.unlink()

        file_obj.delete()
        context.obj['store'].commit()
