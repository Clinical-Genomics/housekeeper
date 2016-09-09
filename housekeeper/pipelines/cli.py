# -*- coding: utf-8 -*-
import logging

import click

from housekeeper.store import get_manager, api
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
    records = mip_analysis(config, force=force)
    case_name = records['case'].name
    old_analysis, old_run = check_existing(case_name, records['analysis'],
                                           records['run'])

    if old_analysis:
        existing_run = api.runs(name=case_name).first()
        is_delivered = 'yes' if existing_run.delivered_at else 'no'
        is_archived = 'yes' if existing_run.archived_at else 'no'
        if old_run:
            click.echo("identical run detected: {}".format(case_name))
            if not force:
                context.abort()
            else:
                manager.delete_commit(old_run)

        click.echo("analysis already loaded: {}".format(case_name))
        click.echo("delivered: {}, archived: {}".format(is_delivered, is_archived))
        question = "old analysis run detected, replace it?"
        if force or yes or click.confirm(question):
            # delete it!
            api.delete(old_analysis)
            manager.commit()
        else:
            context.abort()

    try:
        commit_analysis(manager, **records)
        click.echo("added new analysis: {}".format(case_name))
        sample_ids = ', '.join(sample.name for sample in
                               records['analysis'].samples)
        click.echo("including samples: {}".format(sample_ids))
    except AnalysisConflictError:
        click.echo("analysis output not removed: {}".format(case_name))
