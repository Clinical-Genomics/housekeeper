# -*- coding: utf-8 -*-
import click

from housekeeper.store import get_manager
from .mip import analysis as mip_analysis
from .general import commit_analysis


@click.group()
@click.pass_context
def add(context):
    """Add analyses from different pipelines."""
    context.obj['db'] = get_manager(context.obj['database'])


@add.command()
@click.argument('config', type=click.Path(exists=True))
@click.pass_context
def mip(context, config):
    """Add MIP analysis."""
    new_analysis = mip_analysis(config)
    commit_analysis(context.obj['db'], new_analysis)
