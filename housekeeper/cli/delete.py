"""Module for deleting via CLI"""
import shutil
from pathlib import Path

import click


@click.group()
def delete():
    """Delete things in the database."""


@delete.command()
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.argument("bundle_name")
@click.pass_context
def bundle(context, yes, bundle_name):
    """Delete the latest bundle version."""
    store = context.obj["store"]
    bundle_obj = store.bundle(bundle_name)
    if bundle_obj is None:
        click.echo(click.style("bundle not found", fg="red"))
        context.abort()
    version_obj = bundle_obj.versions[0]
    if version_obj.included_at:
        question = f"remove bundle version from file system and database: {version_obj.full_path}"
    else:
        question = (
            f"remove bundle version from database: {version_obj.created_at.date()}"
        )
    if not (yes or click.confirm(question)):
        context.abort()

    if version_obj.included_at:
        shutil.rmtree(version_obj.full_path, ignore_errors=True)
    version_obj.delete()
    store.commit()
    click.echo(f"version deleted: {version_obj.full_path}")


@delete.command()
@click.option("--yes", is_flag=True, help="skip checks")
@click.option("-t", "--tag", multiple=True, help="file tag")
@click.option("-b", "--bundle-name", help="bundle name")
@click.option("-a", "--before", help="version created before...")
@click.option(
    "-n", "--notondisk", is_flag=True, help="rm db entry from files not on disk"
)
@click.option(
    "-l", "--list-files", is_flag=True, help="lists files that will be deleted"
)
@click.option(
    "-L", "--list-files-verbose", is_flag=True, help="lists additional information"
)
@click.pass_context
def files(
    context, yes, tag, bundle_name, before, notondisk, list_files, list_files_verbose
):
    """Delete files based on tags."""
    store = context.obj["store"]
    file_objs = []
    if not (tag or bundle_name):
        click.echo("Please specify a bundle or a tag")
        context.abort()

    if bundle_name:
        bundle_obj = store.bundle(bundle_name)
        if bundle_obj is None:
            click.echo(click.style("bundle not found", fg="red"))
            context.abort()

    query = store.files_before(bundle=bundle_name, tags=tag, before=before)

    if notondisk:
        file_objs = set(query) - store.files_ondisk(query)
    else:
        file_objs = query.all()

    nr_files = 0
    for nr_files, file_obj in enumerate(file_objs, 1):
        if list_files_verbose:
            tags = ", ".join(tag.name for tag in file_obj.tags)
            click.echo(
                f"{click.style(str(file_obj.id), fg='blue')} | {file_obj.full_path} | "
                f"{click.style(tags, fg='yellow')}"
            )
        elif list_files:
            click.echo(file_obj.full_path)
        else:
            continue

    if nr_files == 0:
        click.echo(click.style("no files found", fg="red"))
        context.abort()

    if not (
        yes or click.confirm(f"Are you sure you want to delete {len(file_objs)} files?")
    ):
        context.abort()

    for file_obj in file_objs:
        if yes or click.confirm(
            f"remove file from disk and database: {file_obj.full_path}"
        ):
            file_obj_path = Path(file_obj.full_path)
            if file_obj.is_included and (
                file_obj_path.exists() or file_obj_path.is_symlink()
            ):
                file_obj_path.unlink()
            file_obj.delete()
            store.commit()
            click.echo(f"{file_obj.full_path} deleted")


@delete.command("file")
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.argument("file_id", type=int)
@click.pass_context
def file_cmd(context, yes, file_id):
    """Delete a file."""
    store = context.obj["store"]
    file_obj = store.File.get(file_id)
    if not file_obj:
        click.echo(click.style("file not found", fg="red"))
        context.abort()

    if file_obj.is_included:
        question = f"remove file from file system and database: {file_obj.full_path}"
    else:
        question = f"remove file from database: {file_obj.full_path}"

    if yes or click.confirm(question):
        if file_obj.is_included and Path(file_obj.full_path).exists():
            Path(file_obj.full_path).unlink()

        file_obj.delete()
        store.commit()
        click.echo("file deleted")
