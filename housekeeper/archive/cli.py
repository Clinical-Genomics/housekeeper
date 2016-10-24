# -*- coding: utf-8 -*-
import logging

import click

from housekeeper.store import api, AnalysisRun
from housekeeper.compile.cli import compile as compile_cmd
from .core import archive_run
from housekeeper.cli.utils import run_orabort

log = logging.getLogger(__name__)


@click.command()
@click.option('-d', '--date', help="date of the particular run")
@click.option("-f", "--force", is_flag=True, help="skip checks")
@click.argument('case_name')
@click.pass_context
def archive(context, date, force, case_name):
    """Archive compiled assets to PDC."""
    manager = api.manager(context.obj['database'])
    run_obj = run_orabort(context, case_name, date)
    if not run_obj.compiled_at:
        log.warn("run not compiled yet: %s", case_name)
        if force or click.confirm("do you want to compile the run?"):
            date_str = run_obj.analyzed_at.date().isoformat()
            context.invoke(compile_cmd, date=date_str, force=True,
                           case_name=case_name)
            # refresh the run object
            run_obj = AnalysisRun.query.get(run_obj.id)
        else:
            context.abort()

    if force or click.confirm("are you sure you want to archive the run?"):
        archive_run(run_obj, force=force)
        manager.commit()
