"""Code for CLI get"""

import json as jsonlib
import logging

import click
from rich.console import Console

from housekeeper.services.file_service.file_service import FileService
from housekeeper.services.file_report_service.file_report_service import FileReportService
from housekeeper.store.api import schema
from housekeeper.store.models import Version
from housekeeper.store.store import Store

from .tables import (
    get_bundles_table,
    get_tags_table,
    get_versions_table,
)

LOG = logging.getLogger(__name__)


@click.group()
def get():
    """Get info from database"""


@get.command("bundle")
@click.argument("bundle-name", required=False)
@click.option("-i", "--bundle-id", type=int, help="Search for a bundle with bundle id")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.option(
    "-c",
    "--compact",
    is_flag=True,
    help="print compact filenames IFF verobe flag present",
)
@click.pass_context
def bundle_cmd(context, bundle_name, bundle_id, json, compact):
    """Get bundle information from database"""
    store: Store = context.obj["store"]
    bundles = store.bundles()

    if bundle_name:
        bundle = store.get_bundle_by_name(bundle_name=bundle_name)
        bundles = [bundle] if bundle else []

    if bundle_id:
        bundle = store.get_bundle_by_id(bundle_id=bundle_id)
        bundles = [bundle] if bundle else []

    if not bundles:
        LOG.info("Could not find any bundles")
        return
    template = schema.BundleSchema()
    result = []
    for bundle in bundles:
        result.append(template.dump(bundle))

    if json:
        click.echo(jsonlib.dumps(result, indent=4, sort_keys=True))
        return
    console = Console()
    console.print(get_bundles_table(result))
    for bundle in bundles:
        if len(bundle.versions) == 0:
            LOG.info("No versions found for bundle %s", bundle.name)
            return
        version_obj = bundle.versions[0]
        context.invoke(version_cmd, version_id=version_obj.id, verbose=True, compact=compact)


@get.command("version")
@click.option("-b", "--bundle-name", help="Fetch all versions from a bundle")
@click.option("-i", "--version-id", type=int, help="Fetch a specific version")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.option("-v", "--verbose", is_flag=True, help="print additional information")
@click.option(
    "-c",
    "--compact",
    is_flag=True,
    help="print compact filenames IFF verobe flag present",
)
@click.pass_context
def version_cmd(context, bundle_name, json, version_id, verbose, compact):
    """Get versions from database"""
    store: Store = context.obj["store"]
    if not (bundle_name or version_id):
        LOG.info("Please select a bundle or a version")
        return
    if bundle_name:
        bundle = store.get_bundle_by_name(bundle_name=bundle_name)
        if not bundle:
            LOG.info("Could not find bundle %s", bundle_name)
            return
        version_objs = bundle.versions

    if version_id:
        version: Version = store.get_version_by_id(version_id=version_id)
        if not version:
            LOG.warning("Could not find version %s", version_id)
            raise click.Abort
        version_objs = [version]

    version_template = schema.VersionSchema()
    result = []
    for version_obj in version_objs:
        bundle = store.get_bundle_by_id(bundle_id=version_obj.bundle_id)
        res = version_template.dump(version_obj)
        res["bundle_name"] = bundle.name
        result.append(res)

    if json:
        click.echo(jsonlib.dumps(result))
        return

    console = Console()
    console.print(get_versions_table(result))
    if not verbose:
        return

    for version_obj in version_objs:
        context.invoke(files_cmd, version_id=version_obj.id, verbose=True, compact=compact)


@get.command("file")
@click.option("-t", "--tag", "tag_names", multiple=True, help="filter by file tag")
@click.option("-v", "--version", "version_id", type=int, help="filter by version of the bundle")
@click.option("-V", "--verbose", is_flag=True, help="print additional information")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.option("-c", "--compact", is_flag=True, help="print compact filenames")
@click.argument("bundle", required=False)
@click.pass_context
def files_cmd(
    context,
    tag_names: list[str],
    version_id: int,
    verbose: bool,
    bundle: str,
    json: bool,
    compact: bool,
):
    """Get files from database"""
    file_service: FileService = context.obj["file_service"]
    output_service: FileReportService = context.obj["file_report_service"]

    output_service.compact = compact
    output_service.json = json

    local = file_service.get_local_files(bundle=bundle, tags=tag_names, version_id=version_id)
    remote = file_service.get_remote_files(bundle=bundle, tags=tag_names, version_id=version_id)

    output_service.log_file_table(files=local, header="Local files", verbose=verbose)
    output_service.log_file_table(files=remote, header="Remote files", verbose=False)


@get.command("tag")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.option("-n", "--name", multiple=True, help="Specify a tag name")
@click.pass_context
def tag_cmd(context, json, name):
    """Get the tags from database"""
    store: Store = context.obj["store"]
    LOG.info("Fetch tags")
    tag_objs = store.get_tags()
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
