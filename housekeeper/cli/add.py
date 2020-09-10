"""Module for adding via CLI"""
import datetime as dt
import logging
from logging import Logger
from pathlib import Path
from typing import List

import click

from housekeeper.date import get_date
from housekeeper.files import load_json, validate_input

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
@click.pass_context
def bundle_cmd(context: click.Context, bundle_name: str, json: str):
    """Add a new bundle."""
    LOG.info("Running add bundle")
    store = context.obj["store"]

    validate_args(arg=bundle_name, json=json, arg_name="bundle_name")

    data = {}
    data["name"] = bundle_name
    data["created_at"] = str(dt.datetime.now())
    # This is to preserve the behaviour of adding a bundle without providing all information
    if json:
        data = load_json(json)

    bundle_name = data["name"]
    if store.bundle(bundle_name):
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
    store.add_commit(new_bundle)
    new_version.bundle = new_bundle
    store.add_commit(new_version)
    LOG.info("new bundle added: %s (%s)", new_bundle.name, new_bundle.id)


@add.command("file")
@click.option("-t", "--tag", "tags", multiple=True, help="tag to associate the file by")
@click.option("-b", "--bundle-name", help="name of bundle that file should be added to")
@click.option("-j", "--json", help="json formated input")
@click.argument("path", required=False)
@click.pass_context
def file_cmd(context: click.Context, tags: List[str], bundle_name: str, json: str, path: str):
    """Add a file to the latest version of a bundle."""
    LOG.info("Running add file")
    store = context.obj["store"]
    validate_args(arg=path, json=json, arg_name="path")

    data = {}
    if json:
        data = load_json(json)
        validate_input(data, input_type="file")

    file_path = Path(data.get("path", path))
    if not file_path.exists():
        LOG.warning("File: %s does not exist", file_path)
        raise click.Abort

    bundle_name = data.get("bundle", bundle_name)
    bundle_obj = store.bundle(bundle_name)
    if bundle_obj is None:
        LOG.warning("unknown bundle: %s", bundle_name)
        raise click.Abort

    tags = data.get("tags", tags)

    new_file = store.add_file(file_path=file_path, bundle=bundle_obj, tags=tags)
    store.add_commit(new_file)
    LOG.info("new file added: %s (%s)", new_file.path, new_file.id)


@add.command("version")
@click.option("-j", "--json", help="Input in json format")
@click.option("--created-at", help="Date when created")
@click.argument("bundle_name", required=False)
@click.pass_context
def version_cmd(context: click.Context, bundle_name: str, created_at: str, json: str):
    """Add a new version to a bundle."""
    LOG.info("Running add version")
    store = context.obj["store"]

    validate_args(arg=bundle_name, json=json, arg_name="bundle_name")

    data = {}
    data["bundle_name"] = bundle_name
    data["created_at"] = created_at
    if json:
        data = load_json(json)
        bundle_name = data["bundle_name"]

    data["created_at"] = data.get("created_at") or str(dt.datetime.now())
    validate_input(data, input_type="version")

    bundle_obj = store.bundle(bundle_name)
    if bundle_obj is None:
        LOG.warning("unknown bundle: %s", bundle_name)
        raise click.Abort

    data["created_at"] = get_date(data.get("created_at"))

    new_version = store.add_version(data, bundle_obj)
    if not new_version:
        LOG.warning("Seems like version already exists for the bundle")
        raise click.Abort

    store.add_commit(new_version)
    LOG.info("new version (%s) added to bundle %s", new_version.id, bundle_obj.name)


@add.command("tag")
@click.argument("tags", nargs=-1)
@click.option("-f", "--file-id", type=int)
@click.pass_context
def tag_cmd(context: click.Context, tags: List[str], file_id: int):
    """Add tags to housekeeper. Use `--file-id` to add tags to existing file"""
    LOG.info("Running add tag")
    store = context.obj["store"]
    file_obj = None
    if len(tags) == 0:
        LOG.warning("No tags provided")
        raise click.Abort

    if file_id:
        file_obj = store.file_(file_id)
        if not file_obj:
            LOG.warning("unable to find file with id %s", file_id)
            raise click.Abort

    for tag_name in tags:
        tag_obj = store.tag(tag_name)

        if not tag_obj:
            LOG.info("%s: tag created", tag_name)
            tag_obj = store.new_tag(tag_name)
            store.add_commit(tag_obj)

        if not file_obj:
            continue

        if tag_obj in file_obj.tags:
            LOG.info("%s: tag already added", tag_name)
            continue

        file_obj.tags.append(tag_obj)

    store.commit()

    if not file_obj:
        return

    all_tags = (tag.name for tag in file_obj.tags)
    LOG.info("file tags: %s", ", ".join(all_tags))
