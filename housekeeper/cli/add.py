"""Module for adding via CLI"""

import datetime as dt
import logging
from logging import Logger
from pathlib import Path
from typing import Generator

import click

from housekeeper.constants import ROOT
from housekeeper.date import get_date
from housekeeper.exc import VersionIncludedError
from housekeeper.files import load_json, validate_input
from housekeeper.include import (
    include_version,
    link_to_relative_path,
    relative_path,
    same_file_exists_in_bundle_directory,
)
from housekeeper.store.models import Bundle, Tag, Version
from housekeeper.store.store import Store

LOG: Logger = logging.getLogger(__name__)


def validate_args(arg: str, json: str, arg_name: str) -> None:
    """Check if input is valid

    One of the arguments has to be specified. Both arguments are not allowed
    """
    if not (arg or json):
        LOG.error("Please input json or %s", arg_name)
        raise click.Abort

    if arg and json:
        LOG.warning("Can not input both json and %s", arg_name)
        raise click.Abort


@click.group()
def add():
    """Add things to the store."""


@add.command("bundle")
@click.argument("bundle_name", required=False)
@click.option("-j", "--json", help="Input json string")
@click.option("-e", "--exclude", help="Use to not include bundle when adding it.", is_flag=True)
@click.pass_context
def bundle_cmd(context: click.Context, bundle_name: str, json: str, exclude: bool):
    """Add a new bundle."""
    LOG.info("Running add bundle")
    store: Store = context.obj["store"]

    validate_args(arg=bundle_name, json=json, arg_name="bundle_name")

    data: dict = {"name": bundle_name, "created_at": str(dt.datetime.now())}
    # This is to preserve the behaviour of adding a bundle without providing all information
    if json:
        data: dict = load_json(json)

    bundle_name = data["name"]
    if store.get_bundle_by_name(bundle_name=bundle_name):
        LOG.warning("bundle name %s already exists", bundle_name)
        raise click.Abort

    validate_input(data, input_type="bundle")
    data["created_at"] = get_date(data.get("created_at"))

    if "files" not in data:
        data["files"] = []

    try:
        new_bundle, new_version = store.add_bundle(data)
    except FileNotFoundError as err:
        LOG.warning("File %s does not exist", err)
        raise click.Abort
    store.session.add(new_bundle)
    new_version.bundle: Bundle = new_bundle
    store.session.add(new_version)
    if not exclude:
        try:
            context_root_dir: str = context.obj[ROOT]
            include_version(global_root=context_root_dir, version_obj=new_version)
        except VersionIncludedError as error:
            LOG.error(error.message)
            raise click.Abort
        new_version.included_at = dt.datetime.now()
    store.session.commit()
    LOG.info("new bundle added: %s (%s)", new_bundle.name, new_bundle.id)


@add.command("file")
@click.option("-t", "--tag", "tags", multiple=True, help="tag to associate the file by")
@click.option("-b", "--bundle-name", help="name of bundle that file should be added to")
@click.option("-j", "--json", help="json formatted input")
@click.option(
    "-kip",
    "--keep-input-path",
    is_flag=True,
    default=False,
    show_default=True,
    help="Flag to use the input path in Housekeeper",
)
@click.argument("path", required=False)
@click.pass_context
def file_cmd(
    context: click.Context,
    tags: list[str],
    bundle_name: str,
    json: str,
    keep_input_path: bool,
    path: str,
):
    """Add a file to the latest version of a bundle."""
    LOG.info("Running add file")
    store: Store = context.obj["store"]
    validate_args(arg=path, json=json, arg_name="path")

    data: dict = {}
    if json:
        data: dict = load_json(json)
        validate_input(data, input_type="file")

    file_path: Path = Path(data.get("path", path))
    if not file_path.exists():
        LOG.warning("File: %s does not exist", file_path)
        raise click.Abort

    bundle_name = data.get("bundle", bundle_name)
    bundle = store.get_bundle_by_name(bundle_name=bundle_name)

    if bundle is None:
        LOG.warning("unknown bundle: %s", bundle_name)
        raise click.Abort

    tags = data.get("tags", tags)
    version: Version = bundle.versions[0]
    if keep_input_path:
        housekeeper_file_path: Path = file_path

    if not same_file_exists_in_bundle_directory(
        file_path=file_path, bundle_root_path=context.obj[ROOT], version=version
    ):
        link_to_relative_path(version=version, file_path=file_path, root_path=context.obj[ROOT])

    housekeeper_file_path: Path = relative_path(version=version, file=file_path)
    new_file = store.add_file(file_path=housekeeper_file_path, bundle=bundle, tags=tags)
    store.session.add(new_file)
    store.session.commit()
    LOG.info("new file added: %s (%s)", new_file.path, new_file.id)


@add.command("version")
@click.option("-j", "--json", help="Input in json format")
@click.option("--created-at", help="Date when created")
@click.argument("bundle_name", required=False)
@click.pass_context
def version_cmd(context: click.Context, bundle_name: str, created_at: str, json: str):
    """Add a new version to a bundle."""
    LOG.info("Running add version")
    store: Store = context.obj["store"]

    validate_args(arg=bundle_name, json=json, arg_name="bundle_name")

    data: dict = {"bundle_name": bundle_name, "created_at": created_at}
    if json:
        data: dict = load_json(json)
        bundle_name = data["bundle_name"]

    data["created_at"] = data.get("created_at") or str(dt.datetime.now())
    validate_input(data, input_type="version")

    bundle = store.get_bundle_by_name(bundle_name=bundle_name)
    if bundle is None:
        LOG.warning("unknown bundle: %s", bundle_name)
        raise click.Abort

    data["created_at"] = get_date(data.get("created_at"))
    new_version = store.add_version(data, bundle)

    if not new_version:
        LOG.warning("Seems like version already exists for the bundle")
        raise click.Abort

    store.session.add(new_version)
    store.session.commit()
    LOG.info("new version (%s) added to bundle %s", new_version.id, bundle.name)


@add.command("tag")
@click.argument("tags", nargs=-1)
@click.option("-f", "--file-id", type=int)
@click.pass_context
def tag_cmd(context: click.Context, tags: list[str], file_id: int):
    """Add tags to housekeeper. Use `--file-id` to add tags to existing file"""
    LOG.info("Running add tag")
    store: Store = context.obj["store"]
    file = None
    if not tags:
        LOG.warning("No tags provided")
        raise click.Abort

    if file_id:
        file = store.get_file_by_id(file_id=file_id)

        if not file:
            LOG.warning(f"unable to find file with id: {file_id}")
            raise click.Abort

    tag_name: str
    for tag_name in tags:
        tag: Tag = store.get_tag(tag_name)

        if not tag:
            LOG.info("%s: tag created", tag_name)
            tag: Tag = store.new_tag(tag_name)
            store.session.add(tag)
            store.session.commit()

        if not file:
            continue

        if tag in file.tags:
            LOG.info("%s: tag already added", tag_name)
            continue

        file.tags.append(tag)

    store.session.commit()

    if not file:
        return

    all_tags: Generator = (tag.name for tag in file.tags)
    LOG.info("file tags: %s", ", ".join(all_tags))
