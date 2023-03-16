"""Module for deleting via CLI"""

import logging
import shutil
from pathlib import Path

import click

from housekeeper.date import get_date

LOG = logging.getLogger(__name__)


@click.group()
def delete():
    """Delete things in the database."""


@delete.command("bundle")
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.argument("bundle_name")
@click.pass_context
def bundle_cmd(context, yes, bundle_name):
    """Delete a empty bundle, that is a bundle without versions"""
    store = context.obj["store"]
    bundle_obj = store.get_bundle_by_name(bundle_name=bundle_name)
    if bundle_obj is None:
        LOG.warning("bundle %s not found", bundle_name)
        raise click.Abort

    if bundle_obj.versions:
        LOG.warning("Can not delete bundle, please remove all versions first")
        raise click.Abort

    question = f"Remove bundle {bundle_obj.name} from database?"
    if not (yes or click.confirm(question)):
        raise click.Abort

    bundle_obj.delete()
    store.commit()
    LOG.info("Bundle deleted: %s", bundle_obj.name)


@delete.command("version")
@click.option("-b", "--bundle-name", help="Fetch all versions from a bundle")
@click.option("-i", "--version-id", type=int, help="Fetch a specific version")
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.pass_context
def version_cmd(context, bundle_name, version_id, yes):
    """Delete a version from database"""
    store = context.obj["store"]
    if not (bundle_name or version_id):
        LOG.info("Please select a bundle or a version")
        raise click.Abort

    if bundle_name:
        bundle_obj = store.get_bundle_by_name(bundle_name=bundle_name)
        if not bundle_obj:
            LOG.info("Could not find bundle %s", bundle_name)
            return
        if len(bundle_obj.versions) == 0:
            LOG.warning("Could not find versions for bundle %s", bundle_name)
            return
        LOG.info("Deleting the latest version of bundle %s", bundle_name)
        version_obj = bundle_obj.versions[0]

    if version_id:
        version = store.version(version_id=version_id)
        if not version:
            LOG.warning("Could not find version %s", version_id)
            raise click.Abort
        bundle_obj = store.get_bundle_by_id(bundle_id=version.bundle_id)
        for ver in bundle_obj.versions:
            if ver.id == version_id:
                version_obj = ver

    if version_obj.included_at:
        question = f"remove bundle version from file system and database: {version_obj.full_path}"
    else:
        question = f"remove bundle version from database: {version_obj.created_at.date()}"

    if not (yes or click.confirm(question)):
        raise click.Abort

    if version_obj.included_at:
        shutil.rmtree(version_obj.full_path, ignore_errors=True)

    version_obj.delete()
    store.commit()
    LOG.info("version deleted: %s", version_obj.full_path)


@delete.command("files")
@click.option("--yes", is_flag=True, help="skip checks")
@click.option("-t", "--tag", multiple=True, help="file tag")
@click.option("-b", "--bundle-name", help="bundle name")
@click.option("-a", "--before", help="version created before...")
@click.option("-n", "--notondisk", is_flag=True, help="rm db entry from files not on disk")
@click.option("-l", "--list-files", is_flag=True, help="lists files that will be deleted")
@click.option("-L", "--list-files-verbose", is_flag=True, help="lists additional information")
@click.pass_context
def files_cmd(context, yes, tag, bundle_name, before, notondisk, list_files, list_files_verbose):
    """Delete files based on tags."""

    validate_delete_options(tag=tag, bundle_name=bundle_name)
    before_date = parse_date(before) if before else None
    store = context.obj["store"]

    if bundle_name:
        validate_bundle_exists(store, bundle_name)

    files = store.files_before(bundle=bundle_name, tags=tag, before_date=before_date)

    if notondisk:
        files = store.get_files_not_on_disk(files)

    if not files:
        LOG.warning("No files found")
        raise click.Abort

    if list_files_verbose:
        list_files_verbosely(files)

    elif list_files:
        list_files_with_full_path(files)

    if not (yes or click.confirm(f"Are you sure you want to delete {len(files)} files?")):
        raise click.Abort

    for file_obj in files:
        if yes or click.confirm(f"remove file from disk and database: {file_obj.full_path}"):
            delete_file(file_obj, store)

def validate_delete_options(tag: str, bundle_name: str):
    """Validate delete options."""
    if not (tag or bundle_name):
        LOG.info(f"Please specify a bundle or a tag")
        raise click.Abort

def validate_bundle_exists(store, bundle_name: str):
    """Validate bundle exists."""
    if not store.get_bundle_by_name(bundle_name=bundle_name):
        LOG.warning(f"Bundle {bundle_name} not found")
        raise click.Abort

def list_files_verbosely(files):
    """List files verbosely."""
    for file in files:
        tags = ", ".join(tag.name for tag in file.tags)
        click.echo(
            f"{click.style(str(file.id), fg='blue')} | {file.full_path} | "
            f"{click.style(tags, fg='yellow')}"
        )

def list_files_with_full_path(files):
    for file in files:
        click.echo(file.full_path)

def delete_file(file, store):
    file_obj_path = Path(file.full_path)
    if file_should_be_unlinked(file):
        file_obj_path.unlink()
    file.delete()
    store.commit()
    LOG.info("%s deleted", file.full_path)

def file_should_be_unlinked(file):
    file_path = Path(file.full_path)
    return file.is_included and (file_path.exists() or file_path.is_symlink())

def parse_date(date: str):
    """Attempt to parse date in two different formats."""
    try:
        return get_date(date)
    except ValueError:
        return get_date(date, "%Y-%m-%d %H:%M:%S")

@delete.command("file")
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.argument("file_id", type=int)
@click.pass_context
def file_cmd(context, yes, file_id):
    """Delete a file."""
    store = context.obj["store"]
    file_obj = store.File.get(file_id)
    if not file_obj:
        LOG.info("file not found")
        raise click.Abort

    if file_obj.is_included:
        question = f"remove file from file system and database: {file_obj.full_path}"
    else:
        question = f"remove file from database: {file_obj.full_path}"

    if yes or click.confirm(question):
        if file_obj.is_included and Path(file_obj.full_path).exists():
            Path(file_obj.full_path).unlink()

        file_obj.delete()
        store.commit()
        LOG.info("file deleted")
