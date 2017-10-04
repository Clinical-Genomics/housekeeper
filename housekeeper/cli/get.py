from typing import List

import click

from housekeeper.store import Store


@click.command()
@click.option('-t', '--tag', 'tags', multiple=True, help='filter by file tag')
@click.option('-v', '--version', type=int, help='filter by version of the bundle')
@click.option('-V', '--verbose', is_flag=True, help='print additional information')
@click.argument('bundle', required=False)
@click.pass_context
def get(context, tags: List[str], version: int, verbose: bool, bundle: str):
    """Get files."""
    store = Store(context.obj['database'], context.obj['root'])
    files = store.files(bundle=bundle, tags=tags, version=version)
    for file_obj in files:
        if verbose:
            tags = ', '.join(tag.name for tag in file_obj.tags)
            click.echo(f"{click.style(str(file_obj.id), fg='blue')} | {file_obj.full_path} | "
                       f"{click.style(tags, fg='yellow')}")
        else:
            click.echo(file_obj.full_path)
