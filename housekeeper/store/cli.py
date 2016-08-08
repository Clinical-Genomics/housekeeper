# -*- coding: utf-8 -*-
import logging

import click
from path import path

from .models import Analysis, Metadata
from .utils import get_assets, get_manager

log = logging.getLogger(__name__)


def delete_analysis(manager, name):
    """Delete an analysis."""
    analysis_obj = Analysis.query.filter_by(name=name).one()
    analysis_obj.delete()
    meta = Metadata.query.first()
    path(meta.analyses_root).joinpath(analysis_obj.name).rmtree_p()
    manager.commit()


def archive_analysis(manager, name):
    """Archive an analysis."""
    analysis_obj = Analysis.query.filter_by(name=name).one()

    # remove all files that aren't marked for archive
    for asset in analysis_obj.assets:
        if not asset.to_archive:
            path(asset.path).remove()
            asset.delete()

    # marked the case as "archived"
    analysis_obj.status = 'archived'
    manager.commit()


@click.command()
@click.argument('name')
@click.pass_context
def archive(context, name):
    """Delete an analysis and files."""
    manager = get_manager(context.obj['database'])
    if click.confirm('Are you sure?'):
        archive_analysis(manager, name)


@click.command()
@click.argument('name')
@click.pass_context
def delete(context, name):
    """Delete an analysis and files."""
    manager = get_manager(context.obj['database'])
    meta = Metadata.query.first()
    analyses_root = path(meta.analyses_root)
    analysis_root = analyses_root.joinpath(name)
    click.echo("you are about to delete: {}".format(analysis_root))
    if click.confirm('Are you sure?'):
        delete_analysis(manager, analyses_root, name)


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


@click.command('list')
@click.option('-c', '--compressed', is_flag=True)
@click.option('-l', '--limit', default=10)
@click.argument('analysis_id', required=False)
@click.pass_context
def list_cmd(context, analysis_id, compressed, limit):
    """List added analyses."""
    get_manager(context.obj['database'])
    query = Analysis.query.order_by(Analysis.analyzed_at)

    if analysis_id:
        log.debug("filter analyses on id pattern: ", analysis_id)
        query = query.filter(Analysis.name.contains(analysis_id))

    if query.first() is None:
        log.warn('sorry, no analyses found')
    else:
        for analysis in query.limit(limit):
            click.echo(analysis.to_json(pretty=not compressed))
