# -*- coding: utf-8 -*-
import datetime
import logging

import click

from housekeeper.cli.utils import run_orabort
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
    run_obj = run_orabort(case_name)
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
    run_obj = run_orabort(context, case_name, date)
    run_root = get_rundir(case_name, run_obj)
    click.echo("you are about to delete: {}".format(run_root))
    if click.confirm('Are you sure?'):
        api.delete(run_obj)
        manager.commit()


@click.command()
@click.option('-f', '--force', is_flag=True)
@click.option('-d', '--date', help="date of the particular run")
@click.argument('case_name')
@click.pass_context
def clean(context, force, date, case_name):
    """Clean up files for an analysis."""
    manager = api.manager(context.obj['database'])
    run_obj = run_orabort(context, case_name, date)
    elif force or click.confirm('Are you sure?'):
        api.clean_up(run_obj, force=force)
        manager.commit()
