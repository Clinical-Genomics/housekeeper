# -*- coding: utf-8 -*-
import click
from path import path

from housekeeper.store import Analysis, Metadata, get_manager, Asset, Sample


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


def get_assets(analysis, sample, category):
    """Get files from the database."""
    query = Asset.query
    if analysis:
        query = query.join(Asset.analysis).filter(Analysis.name == analysis)
    if sample:
        query = query.join(Asset.sample).filter(Sample.name == sample)
    if category:
        query = query.filter(Asset.category == category)
    return query


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
    if click.confirm('Are you sure?'):
        delete_analysis(manager, name)


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
