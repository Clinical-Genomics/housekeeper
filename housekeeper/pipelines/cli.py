# -*- coding: utf-8 -*-
import logging

import click
from path import path

from housekeeper.store import api
from housekeeper.store.utils import build_date
from housekeeper.exc import AnalysisConflictError
from .mip import analysis as mip_analysis
from .general import commit_analysis, check_existing

log = logging.getLogger(__name__)


@click.command()
@click.option('-y', '--yes', is_flag=True, help='auto replace old runs')
@click.option('-f', '--force', is_flag=True, help='replace identical runs')
@click.argument('config', type=click.Path(exists=True))
@click.pass_context
def add(context, force, yes, config):
    """Add analyses from different pipelines."""
    manager = api.manager(context.obj['database'])

    log.info("adding analysis with config: %s", config)
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


@click.command()
@click.option('-d', '--date', help="date of the particular run")
@click.option('-c', '--category', required=True)
@click.option('-s', '--sample', help='sample id to link assets to')
@click.option('-a', '--archive-type', type=click.Choice(['data', 'result']))
@click.argument('case_name')
@click.argument('asset_path')
@click.pass_context
def extend(context, date, category, sample, archive_type, case_name, asset_path):
    """Add an additional asset to a run."""
    manager = api.manager(context.obj['database'])
    run_date = build_date(date) if date else None
    run_obj = api.runs(case_name, run_date=run_date).first()
    if run_obj is None:
        log.error("no analysis run found for case: %s", case_name)
        context.abort()
    if sample:
        sample_map = {smpl.name: smpl for smpl in run_obj.samples}
        sample_obj = sample_map[sample]
    else:
        sample_obj = None
    new_asset = api.add_asset(run_obj, asset_path, category, archive_type,
                              sample=sample_obj)
    log.debug("link asset: %s -> %s", new_asset.original_path, new_asset.path)
    path(new_asset.original_path).link(new_asset.path)
    run_obj.append(new_asset)
    manager.commit()
