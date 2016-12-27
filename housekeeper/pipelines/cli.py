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
from housekeeper.pipelines.mip.core import link_asset
from .mip import parse_mip
from .mip2 import parse_mip2
from .mip4 import parse_mip4
from .miparchive import parse as parse_miparchive
from .general import commit_analysis, check_existing
from .mip4.scout import prepare_scout

log = logging.getLogger(__name__)

LOADERS = {'mip': parse_mip, 'mip2': parse_mip2, 'mip4': parse_mip4,
           'miparchive': parse_miparchive}


@click.command()
@click.option('-y', '--yes', is_flag=True, help='auto replace old runs')
@click.option('-f', '--force', is_flag=True, help='skip ALL validations')
@click.option('-r', '--references', type=click.File('r'))
@click.option('-p', '--pipeline', type=click.Choice(LOADERS.keys()),
              default='mip4')
@click.option('--replace', is_flag='replace identical runs')
@click.argument('config', type=click.File('r'))
@click.pass_context
def add(context, force, yes, replace, references, pipeline, config):
    """Add analyses from different pipelines."""
    manager = api.manager(context.obj['database'])
    config_data = yaml.load(config)
    if not references:
        default_ref = "pipelines/references/{}.yaml".format(pipeline)
        references = pkg_resources.resource_string("housekeeper", default_ref)
    reference_data = yaml.load(references)
    loader = LOADERS[pipeline]
    try:
        data = loader(config_data, reference_data, force=force)
    except exc.MalformattedPedigreeError as error:
        log.error("bad PED formatting: %s", error.message)
        context.abort()
    except exc.AnalysisNotFinishedError as error:
        log.error("analysis not finished: %s", error.message)
        context.abort()
    except exc.UnsupportedVersionError as error:
        new_or_old = 'old' if pipeline == 'mip' else 'new'
        log.error("pipeline too %s: %s", new_or_old, error.message)
        context.abort()

    records = link_records(data)
    case_name = records['case'].name
    old_run = check_existing(case_name, records['run'])
    if old_run:
        message = "identical run detected: {}".format(case_name)
        if force or replace:
            log.warn(message)
            api.delete(context.obj['root'], old_run)
            manager.commit()
        else:
            log.error(message)
            context.abort()

    try:
        commit_analysis(manager, context.obj['root'], records['case'],
                        records['run'])
        click.echo("added new analysis: {}".format(case_name))
        sample_ids = ', '.join(sample.lims_id for sample in
                               records['run'].samples)
        click.echo("including samples: {}".format(sample_ids))
    except exc.AnalysisConflictError:
        click.echo("analysis output not removed: {}".format(case_name))


def link_records(data):
    """Fetch existing information."""
    case_obj = api.case(data['case'])
    if case_obj is None:
        raise ValueError("case not found: {}".format(data['case']))
    for sample_id in data['samples']:
        sample_obj = api.sample(sample_id)
        if sample_obj is None:
            raise ValueError("sample not found: {}".format(sample_id))
        data['run'].samples.append(sample_obj)

    for new_asset, sample_id in data['assets']:
        link_asset(data['run'], new_asset, sample=sample_id)
    return {'case': case_obj, 'run': data['run']}


@click.command()
@click.option('--no-link', is_flag=True, help='skip hard linking')
@click.option('-d', '--date', help="date of the particular run")
@click.option('-c', '--category', required=True)
@click.option('-s', '--sample', help='sample id to link assets to')
@click.option('-a', '--archive-type', type=click.Choice(['data', 'result']))
@click.argument('case_name')
@click.argument('asset_path')
@click.pass_context
def extend(context, no_link, date, category, sample, archive_type, case_name,
           asset_path):
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

    root_path = context.obj['root']
    run_root = get_rundir(root_path, run_obj.case.name, run_obj)
    filename = new_asset.basename()
    if no_link:
        new_path = asset_path
    else:
        new_path = run_root.joinpath(filename)
        log.debug("link asset: %s -> %s", new_asset.original_path, new_path)
        path(new_asset.original_path).link(new_path)

    new_asset.path = new_path
    run_obj.assets.append(new_asset)
    log.info("add asset: %s", new_asset.path)
    manager.commit()


@click.command()
@click.option('-m', '--madeline-exe', type=click.Path(exists=True))
@click.option('-d', '--date', help="date of the particular run")
@click.option('-r', '--replace', is_flag=True)
@click.argument('case_name')
@click.pass_context
def scout(context, madeline_exe, date, replace, case_name):
    """Prepare a config and files for Scout."""
    madeline_exe = madeline_exe or context.obj['madeline_exe']
    manager = api.manager(context.obj['database'])
    root_path = context.obj['root']
    run_obj = run_orabort(context, case_name, date)
    if not run_obj.pipeline_version.startswith('v4'):
        log.error("unsupported pipeline version: %s", run_obj.pipeline_version)
        context.abort()

    existing_conf = (api.assets(category='scout-config', run_id=run_obj.id)
                        .first())
    if existing_conf:
        if replace:
            log.info("deleting existing scout config: %s", existing_conf.path)
            api.delete_asset(existing_conf)
            existing_mad = (api.assets(category='madeline', run_id=run_obj.id)
                               .first())
            if existing_mad:
                log.info("deleting existing madeline: %s", existing_mad.path)
                api.delete_asset(existing_mad)
            manager.commit()
        else:
            log.error("scout config already generated")
            context.abort()

    prepare_scout(run_obj, root_path, madeline_exe)
    manager.commit()
