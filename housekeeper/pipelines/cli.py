# -*- coding: utf-8 -*-
import logging
import pkg_resources

import click
from path import path
import yaml

from housekeeper.store import api
from housekeeper.store.utils import get_rundir
from housekeeper.cli.utils import run_orabort
from housekeeper import exc
from .mip import parse_mip
from .mip2 import parse as parse_mip2
from .miparchive import parse as parse_miparchive
from .general import commit_analysis, check_existing

log = logging.getLogger(__name__)

LOADERS = {'mip': parse_mip, 'mip2': parse_mip2,
           'miparchive': parse_miparchive}


@click.command()
@click.option('-y', '--yes', is_flag=True, help='auto replace old runs')
@click.option('-f', '--force', is_flag=True, help='replace identical runs')
@click.option('-r', '--references', type=click.File('r'))
@click.option('-p', '--pipeline', type=click.Choice(LOADERS.keys()),
              default='mip')
@click.argument('config', type=click.File('r'))
@click.pass_context
def add(context, force, yes, references, pipeline, config):
    """Add analyses from different pipelines."""
    manager = api.manager(context.obj['database'])
    config_data = yaml.load(config)
    if not references:
        default_ref = "pipelines/references/{}.yaml".format(pipeline)
        references = pkg_resources.resource_string("housekeeper", default_ref)
    reference_data = yaml.load(references)
    loader = LOADERS[pipeline]
    try:
        records = loader(config_data, reference_data, force=force)
    except (exc.UnsupportedVersionError, exc.AnalysisNotFinishedError):
        context.abort()
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
    except exc.AnalysisConflictError:
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
    run_obj = run_orabort(context, case_name, date)
    if sample:
        sample_map = {smpl.name: smpl for smpl in run_obj.samples}
        sample_obj = sample_map[sample]
    else:
        sample_obj = None
    new_asset = api.add_asset(run_obj, asset_path, category, archive_type,
                              sample=sample_obj)

    run_root = get_rundir(run_obj.case.name, run_obj)
    filename = new_asset.basename()
    new_path = run_root.joinpath(filename)
    new_asset.path = new_path

    log.debug("link asset: %s -> %s", new_asset.original_path, new_asset.path)
    path(new_asset.original_path).link(new_asset.path)
    run_obj.assets.append(new_asset)
    log.info("add asset: %s", new_asset.path)
    manager.commit()
