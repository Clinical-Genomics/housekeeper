"""Code for CLI get"""
import json as jsonlib
import logging
from typing import List

import click
from rich.console import Console

from housekeeper.store.api import schema

from .tables import get_bundles_table, get_files_table, get_tags_table, get_versions_table

LOG = logging.getLogger(__name__)


@click.group()
def get():
    """Get info from database"""


@get.command("tag")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.option("-n", "--name", multiple=True, help="Specify a tag name")
@click.pass_context
def tag_cmd(context, json, name):
    """Get the tags from database"""
    store = context.obj["store"]
    LOG.info("Fetch tags")
    tag_objs = store.tags()
    template = schema.TagSchema()
    result = []
    for tag_obj in tag_objs:
        if name and (tag_obj.name not in name):
            continue
        LOG.debug("Use tag %s", tag_obj.name)
        result.append(template.dump(tag_obj))
    if not result:
        LOG.info("Could not find any of the specified tags [%s]", ", ".join(name))
        return
    if json:
        click.echo(jsonlib.dumps(result))
        return
    console = Console()
    console.print(get_tags_table(result))


@get.command("bundles")
@click.option("-n", "--bundle-name", help="Search for a bundle with name")
@click.option("-i", "--bundle-id", type=int, help="Search for a bundle with bundle id")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.pass_context
def bundle_cmd(context, bundle_name, bundle_id, json):
    """Get bundle from database"""
    store = context.obj["store"]
    bundle_objs = store.bundles()
    if bundle_name or bundle_id:
        bundle_obj = store.bundle(name=bundle_name, bundle_id=bundle_id)
        bundle_objs = [bundle_obj] if bundle_obj else []
    if not bundle_objs:
        LOG.info("Could not find any bundles")
    template = schema.BundleSchema()
    result = []
    for bundle_obj in bundle_objs:
        result.append(template.dump(bundle_obj))

    if json:
        click.echo(jsonlib.dumps(result))
        return
    console = Console()
    console.print(get_bundles_table(result))


@get.command("version")
@click.option("-b", "--bundle-name", help="Fetch all versions from a bundle")
@click.option("-i", "--version-id", type=int, help="Fetch a specific version")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.option("-v", "--verbose", is_flag=True, help="print additional information")
@click.pass_context
def version_cmd(context, bundle_name, json, version_id, verbose):
    """Get versions from database"""
    store = context.obj["store"]
    if not (bundle_name or version_id):
        LOG.info("Please select a bundle or a version")
        return
    if bundle_name:
        bundle = store.bundle(name=bundle_name)
        if not bundle:
            LOG.info("Could not find bundle %s", bundle)
            return
        version_objs = bundle.versions

    if version_id:
        version_objs = [store.Version.get(version_id)]

    version_template = schema.VersionSchema()
    result = []
    for version_obj in version_objs:
        bundle_obj = store.bundle(bundle_id=version_obj.bundle_id)
        res = version_template.dump(version_obj)
        res["bundle_name"] = bundle_obj.name
        result.append(res)

    if json:
        click.echo(jsonlib.dumps(result))
        return

    console = Console()
    console.print(get_versions_table(result))
    if not verbose:
        return

    for version_obj in version_objs:
        context.invoke(files_cmd, version=version_obj.id)


@get.command("files")
@click.option("-t", "--tag", "tags", multiple=True, help="filter by file tag")
@click.option("-v", "--version", type=int, help="filter by version of the bundle")
@click.option("-V", "--verbose", is_flag=True, help="print additional information")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.argument("bundle", required=False)
@click.pass_context
def files_cmd(context, tags: List[str], version: int, verbose: bool, bundle: str, json: bool):
    """Get files from database"""
    store = context.obj["store"]
    file_objs = store.files(bundle=bundle, tags=tags, version=version)
    template = schema.FileSchema()
    result = []
    for file_obj in file_objs:
        result.append(template.dump(file_obj))

    if json:
        click.echo(jsonlib.dumps(result))
        return
    console = Console()
    console.print(get_files_table(result, verbose=verbose))
