# -*- coding: utf-8 -*-
import datetime
import os
import logging

import click
from path import Path
import yaml

from housekeeper.cli.utils import run_orabort
from .migrate import migrate_root
from .utils import get_rundir
from . import api, Asset, AnalysisRun, Sample

log = logging.getLogger(__name__)


@click.command()
@click.option('-c', '--case')
@click.option('-s', '--sample')
@click.option('-i', '--infer-case', is_flag=True)
@click.option('-t', '--category')
@click.option('-a', '--all', 'all_runs', is_flag=True, default=False)
@click.pass_context
def get(context, case, sample, infer_case, category, all_runs):
    """Ask Housekeeper for a file."""
    api.manager(context.obj['database'])
    if infer_case:
        sample_obj = api.sample(sample)
        if sample_obj is None:
            log.warn('sorry, sample not found')
            context.abort()
        case = sample_obj.run.case.name
        sample = None
    if not all_runs and case:
        # get assets only from latest run
        latest_run = api.runs(case_name=case).first()
        if latest_run is None:
            log.error("no analysis run found: %s", case)
            context.abort()
        run_id = latest_run.id
    else:
        # get assets from all runs
        run_id = None
    assets = api.assets(case_name=case, sample=sample, category=category,
                        run_id=run_id)
    paths = [asset.path for asset in assets]
    output = ' '.join(paths)
    click.echo(output)


@click.command()
@click.option('-b', '--before', help='list runs before a date')
@click.option('-a', '--after', help='list runs after a date')
@click.option('--archived', is_flag=True, help='list only archived runs')
@click.option('-r', '--root', is_flag=True, help='show root path of runs')
@click.option('-l', '--limit', default=20)
@click.pass_context
def runs(context, before, after, archived, limit, root):
    """List runs loaded in the database."""
    api.manager(context.obj['database'])
    root_path = context.obj['root']
    before_date = build_date(before) if before else None
    after_date = build_date(after) if after else None
    run_q = api.runs(before=before_date, after=after_date, archived=archived)
    for run_obj in run_q.limit(limit):
        if root:
            run_root = get_rundir(root_path, run_obj.case.name, run_obj)
            click.echo(run_root)
        else:
            click.echo("{} - {}".format(run_obj.case.name,
                                        run_obj.analyzed_at.date()))


@click.command()
@click.argument('asset_path')
@click.option('-s', '--short', is_flag=True, default=False,
              help='Print only the filename in the sha1sum file')
@click.option('-d', '--dash', is_flag=True, default=False,
              help='Print a dash instead of the filename')
@click.pass_context
def getsha1(context, asset_path, short, dash):
    """Ask Housekeeper for the sha1sum of a file."""
    api.manager(context.obj['database'])
    checksum = api.sha1(asset_path)
    checksum_of = asset_path
    if short:
        checksum_of = os.path.basename(asset_path)
    if dash:
        checksum_of = '-'

    # for some reason we need two spaces
    click.echo("  ".join((checksum, checksum_of)))


@click.command()
@click.option('-d', '--days', default=30)
@click.argument('case_name')
@click.pass_context
def postpone(context, days, case_name):
    """Ask Housekeeper for a file."""
    manager = api.manager(context.obj['database'])
    run_obj = run_orabort(case_name)
    api.postpone(run_obj, time=datetime.timedelta(days=days))
    manager.commit()
    click.echo("analysis will be archived on: {}"
               .format(run_obj.will_cleanup_at))


@click.command()
@click.option('-y', '--yes', is_flag=True, help="skip confirmation")
@click.option('-d', '--date', help="date of the particular run")
@click.argument('case_name')
@click.pass_context
def delete(context, date, yes, case_name):
    """Delete an analysis run and files."""
    manager = api.manager(context.obj['database'])
    run_obj = run_orabort(context, case_name, date)
    root_path = context.obj['root']
    run_root = get_rundir(root_path, case_name, run_obj)
    click.echo("you are about to delete: {}".format(run_root))
    if yes or click.confirm('Are you sure?'):
        api.delete(root_path, run_obj)
        manager.commit()


@click.command()
@click.option('-f', '--force', is_flag=True)
@click.option('-d', '--date', help="date of the particular run")
@click.argument('case_name')
@click.pass_context
def clean(context, force, date, case_name):
    """Clean up files for an analysis."""
    manager = api.manager(context.obj['database'])
    run_obj = run_orabort(context, case_name, date)
    if force or click.confirm('Are you sure?'):
        api.clean_up(context.obj['root'], run_obj, force=force)
        manager.commit()


@click.command()
@click.option('-l', '--limit', default=20)
@click.option('-o', '--offset', default=0)
@click.option('-s', '--since', help='consider runs since date')
@click.option('--older', is_flag=True)
@click.option('-c', '--category', default='bcf-raw')
@click.pass_context
def ls(context, limit, offset, since, older, category):
    """List files from recently added runs."""
    api.manager(context.obj['database'])
    if category == 'samples':
        query = api.samples().join(Sample.run)
    elif category == 'cases':
        query = AnalysisRun.query
    else:
        query = api.assets(category=category).join(Asset.run)

    if older:
        query = query.order_by(AnalysisRun.analyzed_at)
    else:
        query = query.order_by(AnalysisRun.analyzed_at.desc())

    if since:
        date_obj = build_date(since) if since else None
        if older:
            query = query.filter(AnalysisRun.analyzed_at <= date_obj)
        else:
            query = query.filter(AnalysisRun.analyzed_at >= date_obj)
    else:
        query = query.offset(offset).limit(limit)

    if query.first() is None:
        log.warn('sorry, no matching assets found')
        context.abort()

    if category == 'samples':
        # we only consider unqiue samples
        output = set(sample.name for sample in query)
    elif category == 'cases':
        output = set(run.case.name for run in query)
    else:
        # we only consider files from the latest run per case
        cases = set()
        output = []
        for asset in query:
            if asset.run.case_id not in cases:
                output.append(asset.path)
                cases.add(asset.run.case_id)
    click.echo(" ".join(output))


@click.command()
@click.option('-y', '--yes', is_flag=True)
@click.option('-o', '--only-db', is_flag=True)
@click.argument('new_root', type=click.Path())
@click.pass_context
def migrate(context, yes, only_db, new_root):
    """Migrate all assets from one root dir to another."""
    manager = api.manager(context.obj['database'])
    migrate_root(manager, context.obj['root'], new_root, only_db=only_db)

    if 'config' in context.obj:
        config_path = Path(context.obj['config'])
        if yes or click.confirm("update config file?"):
            # update the root in the config
            with config_path.open('w') as out_handle:
                dump = yaml.dump(context.obj, default_flow_style=False,
                                 allow_unicode=True)
                out_handle.write(dump.decode('utf-8'))


def build_date(date_str):
    """Parse date out of string."""
    return datetime.date(*map(int, date_str.split('-')))
