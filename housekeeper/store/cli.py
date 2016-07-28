# -*- coding: utf-8 -*-
import click
from path import path

from housekeeper.store import Analysis, Metadata, get_manager


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
    delete_analysis(manager, name)
