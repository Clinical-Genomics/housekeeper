"""Module for adding via CLI"""
import json as jsonlib
import logging
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import List

import click
from marshmallow.exceptions import ValidationError

from housekeeper.date import get_date
from housekeeper.store.api.schema import (BundleSchema, InputFileSchema,
                                          TagSchema)

LOG = logging.getLogger(__name__)


def load_json(json_str: str) -> dict:
    """Load a json string"""
    LOG.info("Loading json information")
    try:
        data = jsonlib.loads(json_str)
    except JSONDecodeError as err:
        LOG.warning("Something wrong in json string")
        LOG.error(err)
        raise click.Abort
    return data


def validate_input(data: dict, input_type: str):
    """Validate input with the marshmallow schemas"""
    if input_type == "bundle":
        schema = BundleSchema()
    elif input_type == "file":
        schema = InputFileSchema()
    else:
        LOG.warning("Invalid input type %s", input_type)

    formated_data = schema.dump(data)
    try:
        LOG.info("Validate marshmallow schema")
        schema.load(formated_data)
    except ValidationError as err:
        LOG.warning("Input data does not follow the models")
        LOG.error(err)
        raise click.Abort
    LOG.info("Input looks fine")


@click.group()
def add():
    """Add things to the store."""


@add.command("bundle")
@click.argument("bundle_data")
@click.option("-j", "--json", is_flag=True, help="If input is in json format")
@click.pass_context
def bundle_cmd(context, bundle_data, json):
    """Add a new bundle."""
    LOG.info("Running add bundle")
    store = context.obj["store"]
    if not json:
        bundle_name = bundle_data
        if store.bundle(bundle_name):
            LOG.warning("bundle name already exists")
            raise click.Abort
        new_bundle = store.new_bundle(bundle_name)
        store.add_commit(new_bundle)
        context.invoke(
            version_cmd, bundle_name=new_bundle.name, created_at=new_bundle.created_at
        )
        LOG.info("Create a default version")
        new_version = store.new_version(created_at=new_bundle.created_at)
        LOG.debug("Add bundle %s to version %s", new_bundle.id, new_version.id)
        new_version.bundle = new_bundle
        store.add_commit(new_version)
        LOG.info("new bundle added: %s (%s)", new_bundle.name, new_bundle.id)
        return

    data = load_json(bundle_data)

    data["created"] = get_date(data.get("created"))
    if "expires" in data:
        data["expires"] = get_date(data["expires"])
    if "files" not in data:
        data["files"] = []
    schema = BundleSchema()
    bundle_name = data["name"]
    if store.bundle(bundle_name):
        LOG.warning("bundle name already exists")
        raise click.Abort

    new_bundle, new_version = store.add_bundle(result)
    store.add_commit(new_bundle)
    new_version.bundle = new_bundle
    store.add_commit(new_version)


@add.command("file")
@click.option("-t", "--tag", "tags", multiple=True, help="tag to associate the file by")
@click.option("-a", "--archive", is_flag=True, help="mark file to be archived")
@click.option("-b", "--bundle-name", help="name of bundle that file should be added to")
@click.option("-j", "--json", is_flag=True, help="If input is in json format")
@click.argument("path")
@click.pass_context
def file_cmd(context, tags, archive, bundle_name, json, path):
    """Add a file to the latest version of a bundle."""
    LOG.info("Running add file")
    store = context.obj["store"]
    data = {}
    if json:
        data = load_json(path)
        validate_input(data, input_type="file")
        return

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

    new_file = store.add_file(
        file_path=file_path, bundle=bundle_obj, to_archive=archive, tags=tags
    )
    store.add_commit(new_file)
    LOG.info("new file added: %s (%s)", new_file.path, new_file.id)


@add.command("version")
@click.option("-j", "--json", is_flag=True, help="If input is in json format")
@click.option("--created-at", help="Date when created")
@click.argument("bundle_name")
@click.pass_context
def version_cmd(context, bundle_name, created_at, json):
    """Add a new version to a bundle."""
    LOG.info("Running add bundle")
    store = context.obj["store"]
    bundle_obj = store.bundle(bundle_name)
    if bundle_obj is None:
        LOG.warning("unknown bundle: %s", bundle_name)
        raise click.Abort
    store.add_commit(new_file)
    LOG.info("new file added: %s (%s)", new_file.path, new_file.id)


@add.command("tag")
@click.argument("tags", nargs=-1)
@click.option("-j", "--json", is_flag=True, help="If input is in json format")
@click.option("-f", "--file-id", type=int)
@click.pass_context
def tag_cmd(context: click.Context, tags: List[str], json: bool, file_id: int):
    """Add tags ro housekeeper. Use `--file-id` to add tags to existing file"""
    LOG.info("Running add tag")
    store = context.obj["store"]
    file_obj = None
    if len(tags) == 0:
        LOG.warning("No tags provided")
        return

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
