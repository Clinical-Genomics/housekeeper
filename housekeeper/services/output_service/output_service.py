import click
from housekeeper.services.output_service.utils import format_files, get_files_table
from housekeeper.store.models import File
from rich.console import Console
import json as jsonlib


class OutputService:

    def __init__(self):
        self.console = Console()
        self.verbose = False
        self.compact = False
        self.json = False

    def log_file_table(self, files: list[File], header: str) -> None:
        rows = format_files(files)
        table = get_files_table(
            rows=rows, header=header, verbose=self.verbose, compact=self.compact
        )
        self.console.print(table)

        if self.json:
            click.echo(jsonlib.dumps(files))
