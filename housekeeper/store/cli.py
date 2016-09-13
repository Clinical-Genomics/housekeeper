# -*- coding: utf-8 -*-
import datetime
import logging

import click

from .utils import get_assets, get_manager, get_rundir
from . import api

log = logging.getLogger(__name__)


@click.command()
@click.argument('name')
@click.pass_context
def archive(context, name):
    """Delete an analysis and files."""
    manager = get_manager(context.obj['database'])
    run_obj = api.runs(name).first()
    if run_obj is None:
        click.echo("sorry, couldn't find case by that name")
    elif click.confirm('Are you sure?'):
        api.archive(run_obj)
        manager.commit()


@click.command('clean-up')
@click.option('--keep-archive', is_flag=True, default=False)
@click.argument('name')
@click.pass_context
def cleanup(context, keep_archive, name):
    """Clean up files for an analysis."""
    manager = get_manager(context.obj['database'])
    run_obj = api.runs(name).first()
    if run_obj is None:
        click.echo("sorry, couldn't find a case by that name")
    elif click.confirm('Are you sure?'):
        api.clean_up(run_obj, keep_archive=keep_archive)
        manager.commit()


@click.command()
@click.argument('name')
@click.pass_context
def delete(context, name):
    """Delete an analysis run and files."""
    manager = get_manager(context.obj['database'])
    run_obj = api.runs(name).first()
    if run_obj is None:
        click.echo("sorry, couldn't find a case by that name")
    else:
        run_root = get_rundir(name, run_obj)
        click.echo("you are about to delete: {}".format(run_root))
        if click.confirm('Are you sure?'):
            api.delete(run_obj)
            manager.commit()


@click.command()
@click.option('-c', '--case')
@click.option('-s', '--sample')
@click.option('-c', '--category')
@click.pass_context
def get(context, case, sample, category):
    """Ask Housekeeper for a file."""
    get_manager(context.obj['database'])
    assets = get_assets(case, sample, category)
    paths = [asset.path for asset in assets]
    output = ' '.join(paths)
    click.echo(output, nl=False)


@click.command()
@click.option('-d', '--days', default=30)
@click.argument('case_name')
@click.pass_context
def postpone(context, days, case_name):
    """Ask Housekeeper for a file."""
    manager = get_manager(context.obj['database'])
    run_obj = api.runs(case_name).first()
    api.postpone(run_obj, time=datetime.timedelta(days=days))
    manager.commit()
    click.echo("analysis will be archived on: {}"
               .format(run_obj.will_cleanup_at))
