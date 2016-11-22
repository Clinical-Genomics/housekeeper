# -*- coding: utf-8 -*-
from functools import partial

import click
import yaml

from housekeeper.store import api
from housekeeper.parsemip import parse_mipsex


@click.command()
@click.argument('case_id')
@click.argument('existing_data', type=click.File('r'), default='-')
@click.pass_context
def export(context, case_id, existing_data):
    """Export data about a case/run."""
    api.manager(context.obj['database'])
    run_obj = api.runs(case_id).first()
    hk_data = export_data(run_obj)
    existing = yaml.load(existing_data)
    new_data = fillin_data(existing, hk_data)
    raw_dump = yaml.safe_dump(new_data, default_flow_style=False,
                              allow_unicode=True)
    click.echo(raw_dump)


def export_data(run_obj):
    """Export data about a case."""
    get_assets = partial(api.assets, run_id=run_obj.id)
    qc_metrics = api.assets(category='qc').first()

    family_data = {
        # taboo
        'bcf_raw': get_assets(category='gbcf').first().path,

        # loqusdb
        'pedigree': get_assets(category='pedigree').first().path,
        'vcf_research': get_assets(category='vcf-research-bin').first().path,

        # cgstats
        'sampleinfo': get_assets(category='sampleinfo').first().path,
        'qc': qc_metrics.path,
    }

    # get predicted sex
    qcm_data = yaml.load(open(qc_metrics.path, 'r'))
    predicted_sexes = parse_mipsex(qcm_data)

    samples_data = {
        sample.lims_id: {
            # taboo
            'predicted_sex': predicted_sexes[sample.lims_id],

            # chanjo
            'coverage': get_assets(sample=sample.lims_id,
                                   category='coverage').first().path,
        } for sample in run_obj.samples
    }

    return {'family': family_data, 'samples': samples_data}


def fillin_data(existing_data, hk_data):
    """Fill in data about a case with Housekeeper data."""
    # fill in family data
    existing_data.update(hk_data['family'])

    # fill in sample data
    for sample_data in existing_data['samples']:
        new_data = hk_data['samples'][sample_data['id']]
        sample_data.update(new_data)

    return existing_data
