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


@click.command()
@click.argument('name')
@click.pass_context
def delete(context, name):
    """Delete an analysis and files."""
    manager = get_manager(context.obj['database'])
    delete_analysis(manager, name)
