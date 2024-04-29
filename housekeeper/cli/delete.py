"""Module for deleting via CLI"""

import logging
import shutil
from pathlib import Path

import click

from housekeeper.date import get_date
from housekeeper.store.models import File, Tag
from housekeeper.store.store import Store

LOG = logging.getLogger(__name__)


@click.group()
def delete():
    """Delete things in the database."""


@delete.command("bundle")
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.argument("bundle_name")
@click.pass_context
def bundle_cmd(context, yes, bundle_name):
    """Delete a empty bundle, that is a bundle without versions."""
    store: Store = context.obj["store"]
    bundle = store.get_bundle_by_name(bundle_name=bundle_name)
    if bundle is None:
        LOG.warning("bundle %s not found", bundle_name)
        raise click.Abort

    if bundle.versions:
        LOG.warning("Can not delete bundle, please remove all versions first")
        raise click.Abort

    question = f"Remove bundle {bundle.name} from database?"
    if not (yes or click.confirm(question)):
        raise click.Abort

    store.session.delete(bundle)
    store.session.commit()
    LOG.info(f"Deleted bundle {bundle.name}")


@delete.command("version")
@click.option("-b", "--bundle-name", help="Fetch all versions from a bundle")
@click.option("-i", "--version-id", type=int, help="Fetch a specific version")
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.pass_context
def version_cmd(context, bundle_name, version_id, yes):
    """Delete a version from database."""
    store: Store = context.obj["store"]
    if not (bundle_name or version_id):
        LOG.info("Please select a bundle or a version")
        raise click.Abort

    if bundle_name:
        bundle = store.get_bundle_by_name(bundle_name=bundle_name)
        if not bundle:
            LOG.info(f"Could not find bundle {bundle_name}")
            return
        if len(bundle.versions) == 0:
            LOG.warning(f"Could not find versions for bundle {bundle_name}")
            return
        LOG.info(f"Deleting the latest version of bundle {bundle_name}")
        version_obj = bundle.versions[0]

    if version_id:
        version = store.get_version_by_id(version_id=version_id)
        if not version:
            LOG.warning(f"Could not find version {version_id}")
            raise click.Abort
        bundle = store.get_bundle_by_id(bundle_id=version.bundle_id)
        for ver in bundle.versions:
            if ver.id == version_id:
                version_obj = ver

    if version_obj.included_at:
        question = f"Remove bundle version {version_obj.full_path} from file system and database?"
    else:
        question = f"Remove bundle version {version_obj.created_at.date()} from database?"

    if not (yes or click.confirm(question)):
        raise click.Abort

    if version_obj.included_at:
        shutil.rmtree(version_obj.full_path, ignore_errors=True)

    store.session.delete(version_obj)
    store.session.commit()
    LOG.info(f"version deleted: {version_obj.full_path}")


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
    store: Store = context.obj["store"]

    if bundle_name:
        validate_bundle_exists(store=store, bundle_name=bundle_name)

    files = store.get_files_before(bundle_name=bundle_name, tag_names=tag, before_date=before_date)

    if notondisk:
        files = store.get_files_not_on_disk(files=files)

    if not files:
        LOG.warning("No files found")
        raise click.Abort

    if list_files_verbose:
        list_files_verbosely(files=files)

    elif list_files:
        list_files_with_full_path(files=files)

    if not (yes or click.confirm(f"Are you sure you want to delete {len(files)} files?")):
        raise click.Abort

    for file in files:
        if file.archive:
            LOG.warning(
                f"File {file.path} is archived, please delete it with 'cg archive delete-file' instead. Skipping."
            )
            continue
        if yes or click.confirm(f"Remove file from disk and database: {file.full_path}?"):
            delete_file(file=file, store=store)


@delete.command("tag")
@click.option("-n", "--name", help="Name of the tag to delete")
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.pass_context
def tag_cmd(context, yes, name: str):
    """Delete a tag from the database.
    Entries in the file_tag_link table associated with the tag will be removed."""
    store: Store = context.obj["store"]
    tag: Tag | None = store.get_tag(tag_name=name)
    if not tag:
        LOG.warning(f"Tag {name} not found")
        raise click.Abort

    tag_file_count: int = len(tag.files) if tag.files else 0
    question = f"Delete tag {name} with {tag_file_count} associated files?"

    if yes or click.confirm(question):
        store.session.delete(tag)
        store.session.commit()
        LOG.info(f"Tag {name} deleted")


def validate_delete_options(tag: str, bundle_name: str):
    """Validate delete options."""
    if not (tag or bundle_name):
        LOG.info("Please specify a bundle or a tag")
        raise click.Abort


def validate_bundle_exists(store: Store, bundle_name: str):
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


def delete_file(file: File, store: Store):
    file_path = Path(file.full_path)
    if file_should_be_unlinked(file):
        file_path.unlink()

    store.session.delete(file)
    store.session.commit()
    LOG.info(f"{file.full_path} deleted")


def file_should_be_unlinked(file: File):
    """Check if file should be unlinked."""
    file_path = Path(file.full_path)
    return file.is_included and (file_path.exists() or file_path.is_symlink())


def parse_date(date: str):
    """Attempt to parse date in two different formats."""
    try:
        return get_date(date=date)
    except ValueError:
        return get_date(date=date, date_format="%Y-%m-%d %H:%M:%S")


@delete.command("file")
@click.option("-y", "--yes", is_flag=True, help="skip checks")
@click.argument("file_id", type=int)
@click.pass_context
def file_cmd(context, yes, file_id):
    """Delete a file."""
    store: Store = context.obj["store"]
    file = store.get_file_by_id(file_id=file_id)
    if not file:
        LOG.info("file not found")
        raise click.Abort
    if file.archive:
        LOG.warning("File is archived, please delete it with 'cg archive delete-file' instead")
        raise click.Abort

    if file.is_included:
        question = f"Remove file {file.full_path} from file system and database?"
    else:
        question = f"Remove file {file.full_path} from database?"

    if yes or click.confirm(question):
        if file.is_included and Path(file.full_path).exists():
            Path(file.full_path).unlink()

        store.session.delete(file)
        store.session.commit()
        LOG.info("file deleted")
