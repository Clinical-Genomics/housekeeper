"""Code for CLI get"""
import json as jsonlib
import logging
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table

from housekeeper.store.api import schema

LOG = logging.getLogger(__name__)


def get_tags_table(rows: List) -> Table:
    """Return a tag table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Created")
    for tag_obj in rows:
        table.add_row(
            str(tag_obj["id"]),
            tag_obj["name"],
            tag_obj["category"],
            tag_obj["created_at"].split("T")[0],
        )
    return table


def get_files_table(rows: List, verbose=False) -> Table:
    """Return a tag table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("File name")
    table.add_column("Tags")
    if verbose:
        table.add_column("Archive")
    for file_obj in rows:
        file_tags = ", ".join(tag["name"] for tag in file_obj["tags"])
        file_path = Path(file_obj["path"])
        file_name = file_path.name
        if verbose:
            file_name = str(file_path.resolve())
            table.add_row(
                str(file_obj["id"]), file_name, file_tags, str(file_obj["archive"]),
            )
        else:
            table.add_row(str(file_obj["id"]), file_name, file_tags)

    return table


def get_bundles_table(rows: List) -> Table:
    """Return a bundles table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Bundle name")
    table.add_column("Version IDs")
    table.add_column("Created")
    for bundle_obj in rows:
        bundle_versions = ", ".join(
            str(version["id"]) for version in bundle_obj["versions"]
        )
        table.add_row(
            str(bundle_obj["id"]),
            bundle_obj["name"],
            bundle_versions,
            bundle_obj["created_at"].split("T")[0],
        )
    return table


def get_versions_table(rows: List) -> Table:
    """Return a versions table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Bundle name")
    table.add_column("Nr files")
    table.add_column("Included")
    table.add_column("Archived")
    table.add_column("Created")
    table.add_column("Expires")
    for version_obj in rows:
        table.add_row(
            str(version_obj["id"]),
            version_obj["bundle_name"],
            str(len(version_obj["files"])),
            version_obj["included_at"].split("T")[0]
            if version_obj["included_at"]
            else "",
            version_obj["archived_at"].split("T")[0]
            if version_obj["archived_at"]
            else "",
            version_obj["created_at"].split("T")[0]
            if version_obj["created_at"]
            else "",
            version_obj["expires_at"].split("T")[0]
            if version_obj["expires_at"]
            else "",
        )
    return table


@click.group()
def get():
    """Get info from database"""


@get.command("tags")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.option("-n", "--name", multiple=True, help="Specify a tag name")
@click.pass_context
def tag_cmd(context, json, name):
    """Get the tags from database"""
    store = context.obj["store"]

    tag_objs = store.tags()
    template = schema.TagSchema()
    result = []
    for tag_obj in tag_objs:
        if name and (tag_obj.name not in name):
            continue
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
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.pass_context
def bundle_cmd(context, json):
    """Get bundle from database"""
    store = context.obj["store"]
    bundle_objs = store.bundles()
    template = schema.BundleSchema()
    result = []
    for bundle_obj in bundle_objs:
        result.append(template.dump(bundle_obj))

    if json:
        click.echo(jsonlib.dumps(result))
        return
    console = Console()
    console.print(get_bundles_table(result))


@get.command()
@click.argument("bundle")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.pass_context
def versions(context, bundle, json):
    """Get versions from database"""
    store = context.obj["store"]
    bundle_versions = store.versions(bundle)
    version_template = schema.VersionSchema()
    result = []
    for version_obj in bundle_versions:
        bundle_obj = store.bundle(bundle_id=version_obj.bundle_id)
        res = version_template.dump(version_obj)
        res["bundle_name"] = bundle_obj.name
        result.append(res)

    if json:
        click.echo(jsonlib.dumps(result))
        return
    console = Console()
    console.print(get_versions_table(result))


@get.command()
@click.option("-t", "--tag", "tags", multiple=True, help="filter by file tag")
@click.option("-v", "--version", type=int, help="filter by version of the bundle")
@click.option("-V", "--verbose", is_flag=True, help="print additional information")
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.argument("bundle", required=False)
@click.pass_context
def files(
    context, tags: List[str], version: int, verbose: bool, bundle: str, json: bool
):
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
