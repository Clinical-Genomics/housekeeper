import click
from housekeeper.services.file_report_service.utils import format_files, get_files_table
from housekeeper.store.models import File
from rich.console import Console
import json as jsonlib


class FileReportService:

    def __init__(self, verbose: bool = False, compact: bool = False, json: bool = False):
        self.console = Console()
        self.verbose = verbose
        self.compact = compact
        self.json = json

    def log_file_table(
        self, files: list[File], header: str, include_full_path: bool = True
    ) -> None:
        rows = format_files(files)
        table = get_files_table(
            rows=rows,
            header=header,
            verbose=self.verbose,
            compact=self.compact,
            verbose=include_full_path,
        )
        self.console.print(table)

        if self.json:
            click.echo(jsonlib.dumps(rows))
