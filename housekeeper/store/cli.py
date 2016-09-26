# -*- coding: utf-8 -*-
import datetime
import logging

import click

from housekeeper.cli.utils import run_orabort
from .utils import get_rundir
from . import api

log = logging.getLogger(__name__)


@click.command()
@click.option('-c', '--case')
@click.option('-s', '--sample')
@click.option('-i', '--infer-case', is_flag=True)
@click.option('-c', '--category')
@click.pass_context
def get(context, case, sample, infer_case, category):
    """Ask Housekeeper for a file."""
    api.manager(context.obj['database'])
    if infer_case:
        case = api.sample(sample).run.case.name
        sample = None
    assets = api.assets(case_name=case, sample=sample, category=category)
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
@click.option('-y', '--yes', is_flag=True, help="skip confirmation")
@click.option('-d', '--date', help="date of the particular run")
@click.argument('case_name')
@click.pass_context
def delete(context, date, yes, case_name):
    """Delete an analysis run and files."""
    manager = api.manager(context.obj['database'])
    run_obj = run_orabort(context, case_name, date)
    run_root = get_rundir(case_name, run_obj)
    click.echo("you are about to delete: {}".format(run_root))
    if yes or click.confirm('Are you sure?'):
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
    if force or click.confirm('Are you sure?'):
        api.clean_up(run_obj, force=force)
        manager.commit()


@click.command()
@click.option('-p', '--pretty', is_flag=True)
@click.option('-l', '--limit', default=20)
@click.option('-s', '--since', help='consider runs since date')
@click.option('-c', '--category', default='bcf-raw')
@click.pass_context
def ls(context, pretty, limit, since, category):
    """List recently added runs."""
    api.manager(context.obj['database'])
    date_obj = build_date(since) if since else None
    query = api.runs(since=date_obj)
    query = query.limit(limit) if since is None else query
    if query.first() is None:
        log.warn('sorry, no runs found')
    else:
        cases = set()
        asset_paths = []
        for run_obj in query:
            if run_obj.case_id not in cases:
                asset = api.assets(run_id=run_obj.id, category=category).first()
                asset_paths.append(asset.path)
            cases.add(run_obj.case_id)
        click.echo(" ".join(asset_paths))


def build_date(date_str):
    """Parse date out of string."""
    return datetime.date(*map(int, date_str.split('-')))
