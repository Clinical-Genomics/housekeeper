# -*- coding: utf-8 -*-
import logging

import click

from housekeeper.store import api
from housekeeper.store.utils import build_date
from .core import compile_run
from .restore import restore_run, run_fromtar

log = logging.getLogger(__name__)


@click.command()
@click.option('-d', '--date', help="date of the particular run")
@click.argument('case_name')
@click.pass_context
def compile(context, date, case_name):
    """Delete an analysis and files."""
    manager = api.manager(context.obj['database'])
    run_date = build_date(date) if date else None
    run_obj = api.runs(case_name, run_date=run_date).first()
    if run_obj is None:
        log.error("no analysis run found for case: %s", case_name)
        context.abort()
    elif click.confirm('Are you sure?'):
        compile_run(run_obj)
        manager.commit()


@click.command()
@click.argument('archive_type', type=click.Choice(['data', 'result']))
@click.argument('tar_archive', type=click.Path(exists=True))
@click.pass_context
def restore(context, archive_type, tar_archive):
    """Restore analysis run files."""
    manager = api.manager(context.obj['database'])
    run_obj = run_fromtar(tar_archive)
    if run_obj is None:
        log.error('no matching analysis run found')
        context.abort()
    restore_run(run_obj, tar_archive, archive_type)
    manager.commit()
