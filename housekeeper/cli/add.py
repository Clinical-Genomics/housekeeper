"""Module for adding via CLI"""
import json as jsonlib
import logging
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import List

import click
from marshmallow.exceptions import ValidationError

from housekeeper.date import get_date
from housekeeper.store.api.schema import BundleSchema

LOG = logging.getLogger(__name__)


@click.group()
def add():
    """Add things to the store."""


@add.command()
@click.argument("bundle_data")
@click.option("-j", "--json", is_flag=True, help="If input is in json format")
@click.pass_context
def bundle(context, bundle_data, json):
    """Add a new bundle."""
    LOG.info("Running add bundle")
    store = context.obj["store"]
    if not json:
        bundle_name = bundle_data
        new_bundle = store.new_bundle(bundle_name)
        store.add_commit(new_bundle)
        # add default version
        new_version = store.new_version(created_at=new_bundle.created_at)
        new_version.bundle = new_bundle
        store.add_commit(new_version)
    else:
        try:
            LOG.info("Loading json information")
            data = jsonlib.loads(bundle_data)
        except JSONDecodeError as err:
            LOG.warning("Something wrong in json string")
            LOG.error(err)
            raise click.Abort

        data["created"] = get_date(data.get("created"))
        if "expires" in data:
            data["expires"] = get_date(data["expires"])
        if "files" not in data:
            data["files"] = []
        schema = BundleSchema()
        formatet_data = schema.dump(data)
        try:
            LOG.info("Validate marshmallow schema")
            result = schema.load(formatet_data)
        except ValidationError as err:
            LOG.warning("Input data does not follow the models")
            LOG.error(err)
            raise click.Abort
        bundle_name = data["name"]
        if store.bundle(bundle_name):
            LOG.warning("bundle name already exists")
            raise click.Abort

        new_bundle, new_version = store.add_bundle(result)
        store.add_commit(new_bundle)
        new_version.bundle = new_bundle
        store.add_commit(new_version)

    LOG.info("new bundle added: %s (%s)", new_bundle.name, new_bundle.id)


@add.command("file")
@click.option("-t", "--tag", "tags", multiple=True, help="tag to associate the file by")
@click.option("-a", "--archive", is_flag=True, help="mark file to be archived")
@click.argument("bundle_name")
@click.argument("path")
@click.pass_context
def file_cmd(context, tags, archive, bundle_name, path):
    """Add a file to a bundle."""
    LOG.info("Running add file")
    store = context.obj["store"]
    bundle_obj = store.bundle(bundle_name)
    if bundle_obj is None:
        LOG.warning("unknown bundle: %s", bundle_name)
        raise click.Abort
    version_obj = bundle_obj.versions[0]
    new_file = store.new_file(
        path=str(Path(path).absolute()),
        to_archive=archive,
        tags=[
            store.tag(tag_name) if store.tag(tag_name) else store.new_tag(tag_name)
            for tag_name in tags
        ],
    )
    new_file.version = version_obj
    store.add_commit(new_file)
    LOG.info("new file added: %s (%s)", new_file.path, new_file.id)


@add.command()
@click.argument("tags", nargs=-1)
@click.option("-f", "--file-id", "file_id", type=int)
@click.pass_context
def tag(context: click.Context, tags: List[str], file_id: int = None):
    """Add tags to an existing file."""
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
