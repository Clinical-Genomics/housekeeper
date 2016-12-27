# -*- coding: utf-8 -*-
"""Build Scout config from MIP output."""
import logging
from functools import partial

from path import Path
import yaml

from housekeeper.store import api
from housekeeper.store.utils import get_rundir
from . import madeline

SEX_MAP = {'1': 'male', '2': 'female', '0': 'unknown'}
PHENOTYPE_MAP = {'1': 'unaffected', '2': 'affected'}

log = logging.getLogger(__name__)


def prepare_scout(run_obj, root_path, madeline_exe):
    """Prepare files for Scout upload."""
    run_root = Path(get_rundir(root_path, run_obj.case.name, run=run_obj))
    config_data = build_config(run_obj)

    pedigree = api.assets(category='pedigree', run_id=run_obj.id).one()
    madeline_path = build_madeline(pedigree.path, run_root, madeline_exe)
    if madeline_path:
        mad_asset = api.add_asset(run_obj, madeline_path, 'madeline')
        mad_asset.path = str(madeline_path)
        log.info("add madeline asset: %s", mad_asset.path)
        run_obj.assets.append(mad_asset)
        config_data['madeline'] = mad_asset.path

    # save the new scout config
    config_path = Path(run_root).joinpath('scout.conf.yaml')
    with open(config_path, 'w') as out_handle:
        yaml.safe_dump(config_data, out_handle, indent=4,
                       default_flow_style=False)

    scout_asset = api.add_asset(run_obj, config_path, 'scout-config')
    scout_asset.path = config_path
    log.info("add scout config asset: %s", scout_asset.path)
    run_obj.assets.append(scout_asset)


def build_madeline(pedigree, run_root, madeline_exe):
    """Build and add madeline file to the database."""
    try:
        with open(pedigree, 'r') as in_handle:
            svg_content = madeline.run(in_handle, exe=madeline_exe)
        madeline_path = Path(run_root).joinpath('madeline.xml')
        with open(madeline_path, 'w') as out_handle:
            out_handle.write(svg_content)
        return madeline_path
    except (madeline.SinglePedigreeError,
            madeline.MadelineIncompatibleError) as error:
        log.warn("can't visualize pedigree: %s", error.message)
        return None


def build_config(run_obj):
    """Build a Scout config from a MIP run."""
    customer, family = run_obj.case.name.split('-', 1)
    run_asset = partial(api.assets, run_id=run_obj.id)
    vcf = run_asset(category='vcf-clinical-bin').one()
    vcf_sv = run_asset(category='vcf-clinical-sv-bin').one()
    vcf_research = run_asset(category='vcf-research-bin').one()
    vcf_research_sv = run_asset(category='vcf-research-sv-bin').one()
    sampleinfo = run_asset(category='sampleinfo').one()

    # start from pedigree YAML and add additional information
    pedigree_yaml = run_asset(category='pedigree-yaml').one()
    with open(pedigree_yaml.path, 'r') as in_handle:
        data = yaml.load(in_handle)

    with open(sampleinfo.path, 'r') as in_handle:
        si_data = yaml.load(in_handle)
    rank_model = si_data['program']['rankvariant']['rank_model']['version']
    genome_build = (si_data['human_genome_build']['source'] +
                    si_data['human_genome_build']['version'])

    data['vcf_snv'] = vcf.path
    data['vcf_sv'] = vcf_sv.path
    data['rank_model_version'] = float(rank_model)
    data['analysis_date'] = run_obj.analyzed_at
    data['human_genome_build'] = genome_build
    data['vcf_snv_research'] = vcf_research.path
    data['vcf_sv_research'] = vcf_research_sv.path

    for ped_sample in data['samples']:
        lims_id = ped_sample['sample_id']
        bam_file = run_asset(category='bam', sample=lims_id).one()
        ped_sample['bam_path'] = bam_file.path
        if ped_sample['mother'] == 0:
            del ped_sample['mother']
        if ped_sample['father'] == 0:
            del ped_sample['father']

    return data
