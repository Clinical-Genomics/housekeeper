# -*- coding: utf-8 -*-
import datetime
import logging

import click
from path import path

from .models import Analysis, Metadata
from .utils import get_assets, get_manager
from . import api

log = logging.getLogger(__name__)


@click.command()
@click.argument('name')
@click.pass_context
def archive(context, name):
    """Delete an analysis and files."""
    manager = get_manager(context.obj['database'])
    analysis_obj = api.analysis(name)
    if analysis_obj is None:
        click.echo("sorry, couldn't find an analysis by that name")
    elif click.confirm('Are you sure?'):
        api.archive(analysis_obj)
        manager.commit()


@click.command()
@click.argument('name')
@click.pass_context
def delete(context, name):
    """Delete an analysis and files."""
    manager = get_manager(context.obj['database'])
    analysis_obj = api.analysis(name)
    if analysis_obj is None:
        click.echo("sorry, couldn't find an analysis by that name")
    else:
        meta = Metadata.query.first()
        analysis_root = path(meta.analyses_root).joinpath(name)
        click.echo("you are about to delete: {}".format(analysis_root))
        if click.confirm('Are you sure?'):
            api.delete(analysis_obj)
            manager.commit()


@click.command()
@click.option('-a', '--analysis')
@click.option('-s', '--sample')
@click.option('-c', '--category')
@click.pass_context
def get(context, analysis, sample, category):
    """Ask Housekeeper for a file."""
    get_manager(context.obj['database'])
    assets = get_assets(analysis, sample, category)
    paths = [asset.path for asset in assets]
    output = ' '.join(paths)
    click.echo(output, nl=False)


@click.command()
@click.option('-d', '--days', default=30)
@click.argument('analysis_id')
@click.pass_context
def postpone(context, days, analysis_id):
    """Ask Housekeeper for a file."""
    manager = get_manager(context.obj['database'])
    analysis_obj = api.analysis(analysis_id)
    api.postpone(analysis_obj, time=datetime.timedelta(days=days))
    manager.commit()
    click.echo("analysis will be archived on: {}"
               .format(analysis_obj.will_archive_at))


@click.command('list')
@click.option('-c', '--compressed', is_flag=True)
@click.option('-n', '--names', is_flag=True)
@click.option('-l', '--limit', default=10)
@click.argument('analysis_id', required=False)
@click.pass_context
def list_cmd(context, analysis_id, compressed, names, limit):
    """List added analyses."""
    get_manager(context.obj['database'])
    query = Analysis.query.order_by(Analysis.analyzed_at).limit(limit)

    if analysis_id:
        log.debug("filter analyses on id pattern: ", analysis_id)
        query = query.filter(Analysis.name.contains(analysis_id))

    if query.first() is None:
        log.warn('sorry, no analyses found')
    else:
        if names:
            analysis_ids = (analysis.name for analysis in query)
            click.echo(' '.join(analysis_ids))
        else:
            for analysis in query:
                click.echo(analysis.to_json(pretty=not compressed))
