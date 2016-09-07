# -*- coding: utf-8 -*-
import logging

import click

from housekeeper.store import get_manager, api, AnalysisRun
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
@click.option('-y', '--yes', is_flag=True, help='auto replace old runs')
@click.option('-f', '--force', is_flag=True, help='replace identical runs')
@click.argument('config', type=click.Path(exists=True))
@click.pass_context
def mip(context, force, yes, config):
    """Add MIP analysis."""
    log.info("adding analysis with config: %s", config)
    manager = context.obj['db']
    new_analysis, new_run = mip_analysis(config)

    old_analysis, old_run = check_existing(new_analysis, new_run)

    if old_analysis:
        existing_run = (AnalysisRun.query.filter_by(analysis=new_analysis.name)
                                   .first())
        is_delivered = 'yes' if existing_run.delivered_at else 'no'
        is_archived = 'yes' if existing_run.archived_at else 'no'
        if old_run:
            click.echo("identical run detected: {}".format(new_analysis.name))
            if not force:
                context.abort()
            else:
                manager.delete_commit(old_run)

        click.echo("analysis already loaded: {}".format(new_analysis.name))
        click.echo("delivered: {}, archived: {}".format(is_delivered, is_archived))
        question = "old analysis run detected, replace it?"
        if force or yes or click.confirm(question):
            # delete it!
            api.delete(old_analysis)
            manager.commit()
        else:
            context.abort()

    try:
        commit_analysis(manager, new_analysis, new_run)
        click.echo("added new analysis: {}".format(new_analysis.name))
        sample_ids = ', '.join(sample.name for sample in new_analysis.samples)
        click.echo("including samples: {}".format(sample_ids))
    except AnalysisConflictError:
        click.echo("analysis output not removed: {}".format(new_analysis.name))
