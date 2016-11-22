# -*- coding: utf-8 -*-
import logging

import click
import yaml

from housekeeper.store import api

log = logging.getLogger(__name__)


@click.command('mip-sex')
@click.option('-s', '--sample', help='limit to a single sample')
@click.argument('case_id', required=False)
@click.pass_context
def mip_sex(context, sample, case_id):
    """Parse out analysis determined sex of sample."""
    if sample and case_id is None:
        sample_obj = api.sample(sample)
        if sample_obj is None:
            log.warn('sorry, sample not found')
            context.abort()
        case_id = sample_obj.case_id

    qc_metrics = api.assets(case_id, category='qc').first()
    qcm_data = yaml.load(qc_metrics.path)
    sample_sexes = parse_mipsex(qcm_data)
    if sample:
        click.echo(sample_sexes[sample])
    else:
        for sample_id, sex in sample_sexes.items():
            click.echo("{}: {}".format(sample_id, sex))


def parse_mipsex(qcm_data):
    """Parse out sample sex from qc metrics data."""
    samples_sex = parse_samples(qcm_data)
    sexes = {sample_id: sex for sample_id, sex in samples_sex}
    return sexes


def parse_samples(qcm_data):
    """Parse out the relevant sample information."""
    fam_key = qcm_data.keys()[0]
    for segment_id, values in qcm_data[fam_key].items():
        if segment_id != fam_key:
            # sample data entry, find main section
            for sebsection_id, data in values.items():
                if '_lanes_' in sebsection_id:
                    yield segment_id, data['ChanjoSexCheck']['gender']
