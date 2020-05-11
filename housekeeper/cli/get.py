"""Code for CLI get"""
import json as jsonlib
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table

from housekeeper.store import models
from housekeeper.store.api import schema


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


def get_files_table(rows: List) -> Table:
    """Return a tag table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("File name")
    table.add_column("Tags")
    table.add_column("Archive")
    for file_obj in rows:
        file_tags = ", ".join(tag["name"] for tag in file_obj["tags"])
        file_path = Path(file_obj["path"])
        table.add_row(
            str(file_obj["id"]), file_path.name, file_tags, str(file_obj["archive"]),
        )
    return table


def get_bundles_table(rows: List) -> Table:
    """Return a bundles table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Bundle name")
    table.add_column("Versions")
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


@get.command()
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.pass_context
def tags(context, json):
    """Get the tags from database"""
    store = context.obj["store"]

    tag_objs = store.tags()
    template = schema.TagSchema()
    result = []
    for tag_obj in tag_objs:
        result.append(template.dump(tag_obj))
    if json:
        click.echo(jsonlib.dumps(result))
        return
    console = Console()
    console.print(get_tags_table(result))


@get.command()
@click.option("-j", "--json", is_flag=True, help="Output to json format")
@click.pass_context
def bundles(context, json):
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
    console = Console()
    files = store.files(bundle=bundle, tags=tags, version=version)
    template = schema.FileSchema()
    result = []
    for file_obj in files:
        result.append(template.dump(file_obj))

        if verbose:
            tags = ", ".join(tag.name for tag in file_obj.tags)
            click.echo(
                f"{click.style(str(file_obj.id), fg='blue')} | {file_obj.full_path} | "
                f"{click.style(tags, fg='yellow')}"
            )
    if verbose:
        return
    if json:
        click.echo(jsonlib.dumps(result))
        return
    console.print(get_files_table(result))
