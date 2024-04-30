import click
from housekeeper.services.file_report_service.utils import format_files, get_files_table
from housekeeper.store.models import File
from rich.console import Console
import json as jsonlib


class FileReportService:

    def __init__(self, compact: bool = False, json: bool = False):
        self.console = Console()
        self.compact = compact
        self.json = json

    def log_file_table(self, files: list[File], header: str, verbose: bool = False) -> None:
        rows = format_files(files)
        table = get_files_table(
            rows=rows,
            header=header,
            verbose=verbose,
            compact=self.compact,
        )
        self.console.print(table)

        if self.json:
            click.echo(jsonlib.dumps(rows))
