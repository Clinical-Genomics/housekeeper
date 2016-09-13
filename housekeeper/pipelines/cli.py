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
    old_run = check_existing(case_name, records['run'])

    if old_run:
        click.echo("identical run detected: {}".format(case_name))
        if not force:
            context.abort()
        else:
            api.delete(old_run)

    try:
        commit_analysis(manager, **records)
        click.echo("added new analysis: {}".format(case_name))
        sample_ids = ', '.join(sample.name for sample in records['run'].samples)
        click.echo("including samples: {}".format(sample_ids))
    except AnalysisConflictError:
        click.echo("analysis output not removed: {}".format(case_name))
