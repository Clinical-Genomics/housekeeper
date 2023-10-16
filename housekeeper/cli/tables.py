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


def get_files_table(rows: list[dict], verbose=False, compact=False) -> Table:
    """Return a tag table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.title = "[not italic]:scroll:[/] Files table [not italic]:scroll:[/]"
    table.add_column("ID")
    table.add_column("File name")
    table.add_column("Tags")
    if compact:
        rows = squash_names(rows)
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


def squash_names(list_of_files: list[dict]) -> list[dict]:
    """If subsequent elements (filenames) in 'list_of_files' end in an integer- And that integer is
    following the previous- those are squashed when displayed.
    Example:

        ["asdf1.txt", "asdf2.txt"] becomes asdf[1-2].txt'

    Algorithm summary

        Traverse a list of dictionaries, where each dictionary represents
        a file with 'name', 'path' and 'tag', etc. For each name in the list ending
        with integer n, for every subsequent name ending in n+1, n+2, ... n+i displayed
        name wlll be: name[n-i].

        Input list will not be sorted.

        For each element e in the list, e will be searched by regular expression for integers
        at specific location, this is cached for next iteration where a comparision is done. If
        subsequent cache is updated, if not the result is printed. Print will look in the cache
        to check if current iteration has a subsequent integer ending. Tags associated to squashed
        filenames will be sorted and duplicates removed.
    """
    list_of_squashed = []
    tag_list = []
    if list_of_files == []:
        return list_of_squashed
    head = list_of_files[0]
    tail = list_of_files[1:]
    (previous_file, previous_counter, previous_suffix) = _get_suffix(head["path"])
    squash = [previous_counter]
    previous_hkjson = head
    for hk_json in tail + [{"path": ""}]:  # Add padding for final iteration
        (filename, counter, suffix) = _get_suffix(hk_json["path"])
        if counter == str(_to_int(previous_counter) + 1) and (previous_file == filename):
            squash = squash + [counter]
            tag_list = tag_list + (hk_json["tags"])
        else:
            if len(squash) == 1:  # only previous element in list
                list_of_squashed.append(previous_hkjson)
                squash = [counter]
            else:
                squashed_path = (
                    previous_file + "[" + squash[0] + "-" + squash[-1] + "]" + previous_suffix
                )
                previous_hkjson["path"] = squashed_path
                previous_hkjson["full_path"] = squashed_path
                previous_hkjson["tags"] = remove_duplicates(sorted(tag_list, key=lambda i: i["id"]))
                previous_hkjson["id"] = "-"
                list_of_squashed.append(previous_hkjson)
                squash = [counter]
                tag_list = []
        previous_counter = counter
        previous_suffix = suffix
        previous_file = filename
        previous_hkjson = hk_json
    return list_of_squashed


def remove_duplicates(tag_list: list[dict]) -> list[dict]:
    """Remove duoplicate elements from `tag_list`"""
    no_duplicates = []
    for i in tag_list:
        if i not in no_duplicates:
            no_duplicates.append(i)
    return no_duplicates


def _get_suffix(filename):
    """Split a filename if ending with an integer before suffix"""
    # re.split('(\d+)\.\w{3}$', "asdf1.asd")
    parsed = re.split("(\d+)\.(\w{2,3}$)", filename)
    if len(parsed) == 4:
        return (parsed[0], parsed[1], "." + parsed[2])
    return (filename, "", "")


def _to_int(string):
    """Cast to int, empty string becomes 0"""
    if string == "":
        return 0
    return int(string)
