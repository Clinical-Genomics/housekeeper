"""Code for building tables that are displayed in the terminal"""

from pathlib import Path
from typing import List

from rich.table import Table


def get_tags_table(rows: List[dict]) -> Table:
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


def get_files_table(rows: List[dict], verbose=False) -> Table:
    """Return a tag table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.title = "[not italic]:scroll:[/] Files table [not italic]:scroll:[/]"
    table.add_column("ID")
    table.add_column("File name")
    table.add_column("Tags")
    for i, file_obj in enumerate(rows, 1):
        file_tags = ", ".join(tag["name"] for tag in file_obj["tags"])
        file_path = Path(file_obj["path"])
        file_name = file_path.name
        if verbose:
            file_name = file_obj["full_path"]

        if i % 2 == 0:
            table.add_row(str(file_obj["id"]), f"[yellow]{file_name}[/yellow]", file_tags)
        else:
            table.add_row(str(file_obj["id"]), f"[blue]{file_name}[/blue]", file_tags)

    return table


def get_bundles_table(rows: List[dict]) -> Table:
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


def get_versions_table(rows: List[dict]) -> Table:
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
