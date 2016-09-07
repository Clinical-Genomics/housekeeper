# -*- coding: utf-8 -*-
import logging

import click
from path import path

from housekeeper.store import get_manager, api, Metadata
from housekeeper.exc import AnalysisConflictError
from .mip import analysis as mip_analysis
from .general import commit_analysis, check_existing

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
def add(context):
    """Add analyses from different pipelines."""
    context.obj['db'] = get_manager(context.obj['database'])


@add.command()
@click.option('-y', '--yes', help='auto replace old runs')
@click.argument('config', type=click.Path(exists=True))
@click.pass_context
def mip(context, yes, config):
    """Add MIP analysis."""
    log.info("adding analysis with config: %s", config)
    manager = context.obj['db']
    new_analysis, new_run = mip_analysis(config)
    try:
        old_analysis = check_existing(new_analysis, new_run)
    except AnalysisConflictError:
        click.echo("analysis already loaded: {}".format(new_analysis.name))

    if old_analysis:
        if yes or click.confirm("old analysis run detected, replace it?"):
            # delete it!
            meta = Metadata.query.first()
            analysis_root = path(meta.analyses_root).joinpath(old_analysis.name)
            api.delete(old_analysis)
            manager.commit()
        else:
            context.abort()

    try:
        commit_analysis(manager, new_analysis)
        click.echo("added new analysis: {}".format(new_analysis.name))
        sample_ids = ', '.join(sample.name for sample in new_analysis.samples)
        click.echo("including samples: {}".format(sample_ids))
    except AnalysisConflictError:
        click.echo("analysis output not removed: {}".format(new_analysis.name))
