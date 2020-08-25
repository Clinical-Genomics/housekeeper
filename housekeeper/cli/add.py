"""Module for adding via CLI"""
from pathlib import Path
from typing import List

import click


@click.group()
def add():
    """Add things to the store."""


@add.command()
@click.argument("name")
@click.pass_context
def bundle(context, name):
    """Add a new bundle."""
    store = context.obj["store"]
    if store.bundle(name):
        click.echo(click.style("bundle name already exists", fg="yellow"))
        context.abort()
    new_bundle = store.new_bundle(name)
    store.add_commit(new_bundle)

    # add default version
    new_version = store.new_version(created_at=new_bundle.created_at)
    new_version.bundle = new_bundle
    store.add_commit(new_version)

    click.echo(
        click.style(
            f"new bundle added: {new_bundle.name} ({new_bundle.id})", fg="green"
        )
    )


@add.command("file")
@click.option("-t", "--tag", "tags", multiple=True, help="tag to associate the file by")
@click.option("-a", "--archive", is_flag=True, help="mark file to be archived")
@click.argument("bundle_name")
@click.argument("path")
@click.pass_context
def file_cmd(context, tags, archive, bundle_name, path):
    """Add a file to a bundle."""
    store = context.obj["store"]
    bundle_obj = store.bundle(bundle_name)
    if bundle_obj is None:
        click.echo(click.style(f"unknown bundle: {bundle_name}", fg="red"))
        context.abort()
    version_obj = bundle_obj.versions[0]
    path = Path(path)
    if not path.exists():
        click.echo(click.style(f"File {path} does not exist", fg="red"))
        context.abort()

    new_file = store.new_file(
        path=str(path.absolute()),
        to_archive=archive,
        tags=[
            store.tag(tag_name) if store.tag(tag_name) else store.new_tag(tag_name)
            for tag_name in tags
        ],
    )
    new_file.version = version_obj
    store.add_commit(new_file)
    click.echo(
        click.style(f"new file added: {new_file.path} ({new_file.id})", fg="green")
    )


@add.command()
@click.argument("tags", nargs=-1)
@click.option("-f", "--file-id", "file_id", type=int)
@click.pass_context
def tag(context: click.Context, tags: List[str], file_id: int = None):
    """Add tags to an existing file."""
    store = context.obj["store"]
    file_obj = None
    if len(tags) == 0:
        click.echo(click.style("No tags provided", fg="yellow"))
        return

    if file_id:
        file_obj = store.file_(file_id)
        if not file_obj:
            click.echo(click.style("unable to find file", fg="red"))
            context.abort()

    for tag_name in tags:
        tag_obj = store.tag(tag_name)

        if not tag_obj:
            click.echo(click.style(f"{tag_name}: tag created", fg="green"))
            tag_obj = store.new_tag(tag_name)

        if not file_obj:
            continue

        if tag_obj in file_obj.tags:
            click.echo(click.style(f"{tag_name}: tag already added", fg="yellow"))
            continue

        file_obj.tags.append(tag_obj)

    store.commit()

    if not file_obj:
        context.exit()

    all_tags = (tag.name for tag in file_obj.tags)
    click.echo(click.style(f"file tags: {', '.join(all_tags)}", fg="blue"))
