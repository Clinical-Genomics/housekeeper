# -*- coding: utf-8 -*-
import datetime
import logging

import click

from .utils import get_rundir, build_date
from . import api

log = logging.getLogger(__name__)


@click.command()
@click.option('-c', '--case')
@click.option('-s', '--sample')
@click.option('-c', '--category')
@click.pass_context
def get(context, case, sample, category):
    """Ask Housekeeper for a file."""
    api.manager(context.obj['database'])
    assets = api.assets(case, sample, category)
    paths = [asset.path for asset in assets]
    output = ' '.join(paths)
    click.echo(output, nl=False)


@click.command()
@click.option('-d', '--days', default=30)
@click.argument('case_name')
@click.pass_context
def postpone(context, days, case_name):
    """Ask Housekeeper for a file."""
    manager = api.manager(context.obj['database'])
    run_obj = api.runs(case_name).first()
    if run_obj is None:
        log.error("no analysis run found for case: %s", case_name)
        context.abort()
    api.postpone(run_obj, time=datetime.timedelta(days=days))
    manager.commit()
    click.echo("analysis will be archived on: {}"
               .format(run_obj.will_cleanup_at))


@click.command()
@click.argument('case_name')
@click.option('-d', '--date', help="date of the particular run")
@click.pass_context
def delete(context, date, case_name):
    """Delete an analysis run and files."""
    manager = api.manager(context.obj['database'])
    run_date = build_date(date) if date else None
    run_obj = api.runs(case_name, run_date=run_date).first()
    if run_obj is None:
        log.error("no analysis run found for case: %s", case_name)
        context.abort()
    run_root = get_rundir(case_name, run_obj)
    click.echo("you are about to delete: {}".format(run_root))
    if click.confirm('Are you sure?'):
        api.delete(run_obj)
        manager.commit()


@click.command('clean-up')
@click.option('-f', '--force', is_flag=True)
@click.option('-d', '--date', help="date of the particular run")
@click.argument('case_name')
@click.pass_context
def clean(context, force, date, case_name):
    """Clean up files for an analysis."""
    manager = api.manager(context.obj['database'])
    run_date = build_date(date) if date else None
    run_obj = api.runs(case_name, run_date=run_date).first()
    if run_obj is None:
        log.error("no analysis run found for case: %s", case_name)
        context.abort()
    elif force or click.confirm('Are you sure?'):
        api.clean_up(run_obj, force=force)
        manager.commit()
