import re
from pathlib import Path

from rich.table import Table

from housekeeper.store.api import schema
from housekeeper.store.models import File


def format_files(files: list[File]):
    template = schema.FileSchema()
    formatted_files = []
    for file in files:
        formatted_file = template.dump(file)
        formatted_files.append(formatted_file)
    return formatted_files


def get_files_table(rows: list[dict], header: str, verbose=False, compact=False) -> Table:
    """Return a tag table"""
    table = Table(show_header=True, header_style="bold magenta")
    table.title = f"[not italic]:scroll:[/] {header} [not italic]:scroll:[/]"
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
            table.add_row(str(file_obj["id"]), f"[cyan]{file_name}[/cyan]", file_tags)
    return table


def squash_names(list_of_files: list[dict]) -> list[dict]:
    """If subsequent elements (filenames) in 'list_of_files' end in an integer - And that integer is
    following the previous - those are squashed when displayed.
    Example:

        ["asdf1.txt", "asdf2.txt"] becomes asdf[1-2].txt'

    Algorithm summary

        Traverse a list of dictionaries, where each dictionary represents
        a file with 'name', 'path' and 'tag', etc. For each name in the list ending
        with integer n, for every subsequent name ending in n+1, n+2, ... n+i displayed
        name will be: name[n-i].

        The input list will not be sorted.

        For each element e in the list, e will be searched by regular expression for integers
         at a specific location; this is cached for the next iteration where a comparison is done. If
        subsequent cache is updated, if not, the result is printed. Print will look in the cache
        to check if the current iteration has a subsequent integer ending. Tags associated with squashed
        filenames will be sorted and duplicates removed.
    """
    list_of_squashed = []
    tag_list = []
    if not list_of_files:
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
        elif len(squash) == 1:  # only previous element in the list
            list_of_squashed.append(previous_hkjson)
            squash = [counter]
        else:
            squashed_path = f"{previous_file}[{squash[0]}-{squash[-1]}]{previous_suffix}"
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


def _get_suffix(filename: str) -> tuple[str, str, str]:
    """Split a filename if ending with an integer before suffix."""
    parsed: list[str] = re.split(pattern=r"(\d+)\.(\w{2,3}$)", string=filename)
    if len(parsed) == 4:
        return parsed[0], parsed[1], f".{parsed[2]}"
    return filename, "", ""


def _to_int(string):
    """Cast to int, empty string becomes 0"""
    return 0 if string == "" else int(string)
