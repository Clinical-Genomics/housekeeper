from typing import List

import click

from housekeeper.store import Store


@click.command()
@click.option('-t', '--tag', 'tags', multiple=True, help='filter by file tag')
@click.option('-v', '--version', type=int, help='filter by version of the bundle')
@click.argument('bundle', required=False)
@click.pass_context
def get(context, bundle: str, tags: List[str], version: int):
    """Get files."""
    store = Store(context.obj['database'], context.obj['root'])
    files = store.files(bundle=bundle, tags=tags, version=version)
    for file_obj in files:
        click.echo(file_obj.full_path)
