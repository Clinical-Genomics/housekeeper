import click
from housekeeper.cli.tables import get_files_table
from housekeeper.services.output_service.utils import format_files
from housekeeper.store.models import File
from rich.console import Console
import json as jsonlib


class OutputService:

    def __init__(self):
        self.console = Console()

    def output_local_files(
        self, files: list[File], verbose: bool, compact: bool, json: bool
    ) -> None:
        rows = format_files(files)
        header = "Local files"
        table = get_files_table(rows=rows, header=header, verbose=verbose, compact=compact)
        self.console.print(table)

        if json:
            click.echo(jsonlib.dumps(files))

    def output_remote_files(
        self, files: list[File], verbose: bool, compact: bool, json: bool
    ) -> None:
        rows = format_files(files)
        header = "Remote files"
        table = get_files_table(rows=rows, header=header, verbose=verbose, compact=compact)
        self.console.print(table)

        if json:
            click.echo(jsonlib.dumps(files))
