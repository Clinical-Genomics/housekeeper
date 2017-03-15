# -*- coding: utf-8 -*-
import datetime
import os
import logging

import click
from dateutil.parser import parse as parse_date
from path import Path
import yaml

from housekeeper.cli.utils import run_orabort
from housekeeper.constants import EXTRA_STATUSES
from housekeeper.store.models import ExtraRunData
from .migrate import migrate_root
from .utils import get_rundir
from . import api, Asset, AnalysisRun, Sample, Case

RUN_STATUSES = ['analyzed', 'compiled', 'delivered', 'answeredout', 'archived',
                'cleanedup']
SAMPLE_STATUSES = ['received', 'sequenced', 'confirmed']
CASE_STATUSES = RUN_STATUSES + EXTRA_STATUSES

log = logging.getLogger(__name__)


@click.command()
@click.option('-c', '--case', help='filter by case')
@click.option('-s', '--sample', help='filter by sample')
@click.option('-i', '--infer-case', is_flag=True,
              help='filter by related case for a sample')
@click.option('-t', '--category', help='filter by asset category')
@click.option('-a', '--all', 'all_runs', is_flag=True, default=False,
              help='get assets from ALL case runs, not only latest')
@click.pass_context
def get(context, case, sample, infer_case, category, all_runs):
    """Ask Housekeeper for a file."""
    api.manager(context.obj['database'])
    if sample and (case is None):
        sample_obj = api.sample(sample)
        if sample_obj is None:
            log.warn('sorry, sample not found')
            context.abort()
        case = sample_obj.case.name
        if infer_case:
            sample = None

    if not all_runs and (case or sample):
        # get assets only from latest run
        latest_run = api.runs(case_name=case).first()
        if latest_run is None:
            log.error("no analysis run found: %s", case)
            context.abort()
        run_id = latest_run.id
    else:
        # get assets from all runs
        run_id = None

    asset_query = api.assets(case_name=case, sample=sample, category=category,
                             run_id=run_id)
    if asset_query.count() == 0:
        log.error("no matching assets found")
        context.abort()
    else:
        for asset in asset_query:
            click.echo(asset.path)


@click.command()
@click.option('-b', '--before', help='list runs before a date')
@click.option('-a', '--after', help='list runs after a date')
@click.option('--archived/--no-archived', is_flag=True,
              help='list archived/not archived runs')
@click.option('--compiled/--no-compiled', is_flag=True,
              help='list compiled/not compiled runs')
@click.option('--cleaned/--no-cleaned', is_flag=True,
              help='list cleaned up/not cleaned up runs')
@click.option('--to-clean', is_flag=True,
              help='list runs ready to be cleaned up')
@click.option('-o', '--output', type=click.Choice(['root', '', 'sample', 'case']),
              default='case', help='what to output to console')
@click.option('-l', '--limit', default=20)
@click.argument('case_id', required=False)
@click.pass_context
def runs(context, before, after, archived, compiled, cleaned, to_clean,
         limit, output, case_id):
    """List runs loaded in the database."""
    api.manager(context.obj['database'])
    root_path = context.obj['root']
    before_date = parse_date(before) if before else None
    after_date = parse_date(after) if after else None
    run_q = api.runs(case_name=case_id, before=before_date, after=after_date,
                     archived=archived, compiled=compiled, cleaned=cleaned,
                     to_clean=to_clean).limit(limit)
    if run_q.first() is None:
        log.error("no runs found")
        context.abort()
    for run_obj in run_q:
        if output == 'root':
            run_root = get_rundir(root_path, run_obj.case.name, run_obj)
            click.echo(run_root)
        elif output == 'sample':
            for sample in run_obj.samples:
                click.echo(sample.name)
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
@click.option('-d', '--days', default=30, help='days to postpone clean up')
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


@click.group()
@click.pass_context
def delete(context):
    """Delete things from the database."""
    pass


@delete.command('analysis')
@click.option('-y', '--yes', is_flag=True, help="skip manual confirmation")
@click.option('-d', '--date', help="date of the particular run")
@click.argument('case_name')
@click.pass_context
def delete_analysis(context, date, yes, case_name):
    """Delete an analysis run and files."""
    manager = api.manager(context.obj['database'])
    run_obj = run_orabort(context, case_name, date)
    root_path = context.obj['root']
    run_root = get_rundir(root_path, case_name, run_obj)
    click.echo("you are about to delete: {}".format(run_root))
    if yes or click.confirm('Are you sure?'):
        api.delete(root_path, run_obj)
        manager.commit()


@delete.command('sample')
@click.option('-y', '--yes', is_flag=True, help='skip confirmation')
@click.argument('sample_id')
@click.pass_context
def delete_sample(context, yes, sample_id):
    """Delete a sample from the database."""
    manager = api.manager(context.obj['database'])
    sample_obj = api.sample(sample_id)
    if sample_obj is None:
        log.error("sample not found: {}".format(sample_id))
        context.abort()
    click.echo("you are about to delete sample: {} - {}"
               .format(sample_obj.lims_id, sample_obj.id))
    if yes or click.confirm('Are you sure?'):
        sample_obj.delete()
        manager.commit()


@delete.command('case')
@click.option('-y', '--yes', is_flag=True, help='skip confirmation')
@click.argument('case_name')
@click.pass_context
def delete_case(context, yes, case_name):
    """Delete a case from the database."""
    manager = api.manager(context.obj['database'])
    case_obj = api.case(case_name)
    if case_obj is None:
        log.error("case not found: {}".format(case_name))
        context.abort()
    for sample_obj in case_obj.samples:
        log.warn("will remove sample: %s", sample_obj.lims_id)
    for analysis_run in case_obj.runs:
        log.warn("will remove analysis run: %s", analysis_run.analyzed_at.date())
    click.echo("you are about to delete case: {} - {}"
               .format(case_obj.name, case_obj.id))
    if yes or click.confirm('Are you sure?'):
        case_obj.delete()
        manager.commit()


@click.command()
@click.option('-f', '--force', is_flag=True,
              help='auto confirm and override sanity checks')
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
@click.option('-l', '--limit', default=20, help='limit number of results')
@click.option('-o', '--offset', default=0, help='skip initial results')
@click.option('-s', '--since', help='consider runs since date')
@click.option('--older', is_flag=True, help='reverse order of results')
@click.option('-c', '--category', default='bcf-raw',
              help='category of asset to return')
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
        output = (sample.lims_id for sample in query)
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
@click.option('-y', '--yes', is_flag=True, help="answer 'yes' to confirmations")
@click.option('-o', '--only-db', is_flag=True, help='skip migrating assets')
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


@click.command()
@click.option('-s', '--sample-status', type=click.Choice(SAMPLE_STATUSES),
              help='update sample status date')
@click.option('-r', '--run-status', type=click.Choice(RUN_STATUSES),
              help='update run status date')
@click.option('-c', '--extra-status', type=click.Choice(EXTRA_STATUSES),
              help='custom run status')
@click.option('-d', '--date', help='custom date')
@click.option('-n', '--now', is_flag=True, help='set date to "now"')
@click.option('-rd', '--run-date', help='date of a particular run')
@click.argument('identifier')
@click.pass_context
def status(context, date, now, run_date, sample_status, run_status,
           extra_status, identifier):
    """Mark dates for resources."""
    manager = api.manager(context.obj['database'])

    # determine which date to set: custom or now!
    if date:
        status_date = parse_date(date)
    elif now:
        status_date = datetime.datetime.now()
    else:
        status_date = None

    if sample_status:
        # update a date for a sample
        model_obj = api.sample(identifier)
        if model_obj is None:
            click.echo("can't find sample")
            context.abort()
        # types are predefined; no need to check!
        status_type = sample_status
    else:
        # update a date for an analysis run
        model_obj = run_orabort(context, identifier, run_date)
        # types are predefined as well
        status_type = run_status

    if extra_status:
        if model_obj.extra is None:
            log.info("adding extra data record")
            model_obj.extra = ExtraRunData()
            manager.commit()
        extra_date_key = "{}_date".format(extra_status)
        if status_date is None:
            # show a custom date for an analysis run
            current_date = getattr(model_obj.extra, extra_date_key)
        else:
            # update a custom date for a run
            setattr(model_obj.extra, extra_date_key, status_date)
            status_field = extra_status
    else:
        status_field = "{}_at".format(status_type)
        if status_date is None:
            # show a predfined date for a model
            current_date = getattr(model_obj, status_field)
        else:
            # update a predefined date on a model
            setattr(model_obj, status_field, status_date)

    if status_date is None:
        if current_date is None:
            context.abort()
        else:
            click.echo(current_date)
    else:
        log.info("updating %s -> %s", status_field, status_date)
        manager.commit()


@click.command()
@click.option('-l', '--limit', default=20, help='limit number of results')
@click.option('-o', '--offset', default=0, help='skip initial results')
@click.option('-m', '--missing', type=click.Choice(CASE_STATUSES))
@click.option('-v', '--version', help='filter on pipeline version')
@click.option('-r', '--ready', is_flag=True, help='DEPRECATED')
@click.pass_context
def cases(context, limit, offset, missing, version, ready):
    """Display information about cases."""
    api.manager(context.obj['database'])
    query = api.cases(missing=missing, version=version)
    for case in query.offset(offset).limit(limit):
        click.echo(case.name)


@click.command()
@click.option('-l', '--limit', default=20, help='limit number of results')
@click.option('-o', '--offset', default=0, help='skip initial results')
@click.option('-c', '--case', help='return samples related to a case')
@click.option('-m', '--missing', type=click.Choice(SAMPLE_STATUSES))
@click.pass_context
def samples(context, limit, offset, case, missing):
    """Display information about samples."""
    api.manager(context.obj['database'])
    query = api.samples()

    if case:
        query = (query.join(Sample.runs)
                      .join(AnalysisRun.case)
                      .filter(Case.name == case))
    if missing == 'received':
        query = query.filter(Sample.received_at == None)
    elif missing == 'sequenced':
        query = query.filter(Sample.sequenced_at == None)
    elif missing == 'confirmed':
        query = query.filter(Sample.confirmed_at == None)

    for sample in query.offset(offset).limit(limit):
        click.echo(sample.lims_id)


@click.command()
@click.option('-p', '--prioritize', is_flag=True, help='mark high priority')
@click.option('-f', '--flowcell', 'flowcells', multiple=True,
              help='link flowcell to sample')
@click.argument('sample_name')
@click.pass_context
def sample(context, prioritize, flowcells, sample_name):
    """Show or update a sample."""
    manager = api.manager(context.obj['database'])
    sample_obj = api.sample(sample_name)
    if sample_obj is None:
        log.error("no sample found with that name: %s", sample_name)
        context.abort()
    if prioritize:
        sample_obj.priority = True
        manager.commit()
        log.info("prioritized sample!")
    if flowcells:
        for flowcell in flowcells:
            if len(flowcell) != 9:
                log.error("invalid flowcell id: %s", flowcell)
                context.abort()
        flowcell_set = set(flowcells)
        flowcell_set.update(sample_obj.flowcells)
        sample_obj.flowcells = list(flowcell_set)
        manager.commit()
        log.info("updated sample flowcells: %s", sample_obj._flowcells)

    click.echo(sample_obj.to_json(pretty=True))


@click.command('add-sample')
@click.option('-d', '--date', help='date received for sample')
@click.option('-p', '--priority', is_flag=True, help='mark high priority')
@click.argument('customer')
@click.argument('family_id')
@click.argument('lims_id')
@click.pass_context
def add_sample(context, date, priority, customer, family_id, lims_id):
    """Add a new sample to the database."""
    manager = api.manager(context.obj['database'])
    existing_sample = Sample.query.filter_by(lims_id=lims_id).first()
    if existing_sample:
        log.error("sample already exists: %s", lims_id)
        context.abort()
    new_sample = Sample(lims_id=lims_id, priority=priority)
    if date:
        new_sample.received_at = parse_date(date)

    # also add a new case if it doesn't already exist
    case_name = '-'.join([customer, family_id])
    case_obj = api.case(case_name)
    if case_obj is None:
        case_obj = Case(name=case_name, customer=customer, family_id=family_id)
        manager.add(case_obj)
        log.info("added new case: %s", case_name)
    else:
        log.debug("case already exists: %s", case_name)

    # link sample to case
    case_obj.samples.append(new_sample)
    manager.commit()
    log.info("added new sample: %s", lims_id)


@click.command('add-case')
@click.argument('customer')
@click.argument('family_id')
@click.pass_context
def add_case(context, customer, family_id):
    """Add a case to the database."""
    manager = api.manager(context.obj['database'])
    case_name = "-".join([customer, family_id])
    existing_case = api.case(case_name)
    if existing_case:
        log.error("case already exists: %s", case_name)
        context.abort()
    new_case = Case(name=case_name, customer=customer, family_id=family_id)
    manager.add_commit(new_case)
    log.info("added new case: %s", case_name)


def build_date(date_str):
    """Parse date out of string."""
    return datetime.date(*map(int, date_str.split('-')))
