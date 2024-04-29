"""Code for building tables that are displayed in the terminal"""

import re
from pathlib import Path

from rich.table import Table


def get_tags_table(rows: list[dict]) -> Table:
    """Return a tag table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.title = "[not italic]:bookmark:[/] Tags table [not italic]:bookmark:[/]"
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


def get_bundles_table(rows: list[dict]) -> Table:
    """Return a bundles table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.title = "[not italic]:package:[/] Bundle table [not italic]:package:[/]"
    table.add_column("ID")
    table.add_column("Bundle name")
    table.add_column("Version IDs")
    table.add_column("Created")
    for bundle_obj in rows:
        bundle_versions = ", ".join(str(version["id"]) for version in bundle_obj["versions"])
        table.add_row(
            str(bundle_obj["id"]),
            bundle_obj["name"],
            bundle_versions,
            bundle_obj["created_at"].split("T")[0],
        )
    return table


def get_versions_table(rows: list[dict]) -> Table:
    """Return a versions table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.title = "[not italic]:closed_book:[/] Version table [not italic]:closed_book:[/]"
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
            version_obj["included_at"].split("T")[0] if version_obj["included_at"] else "",
            version_obj["archived_at"].split("T")[0] if version_obj["archived_at"] else "",
            version_obj["created_at"].split("T")[0] if version_obj["created_at"] else "",
            version_obj["expires_at"].split("T")[0] if version_obj["expires_at"] else "",
        )
    return table
