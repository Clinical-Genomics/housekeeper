# -*- coding: utf-8 -*-
"""Build Scout config from MIP output."""
import logging

from path import Path
import yaml

from housekeeper.store import api
from housekeeper.store.utils import get_rundir
from . import madeline

SEX_MAP = {'1': 'male', '2': 'female', '0': 'unknown'}
PHENOTYPE_MAP = {'1': 'unaffected', '2': 'affected'}

log = logging.getLogger(__name__)


def prepare_scout(run_obj, madeline_exe):
    """Prepare files for Scout upload."""
    run_root = get_rundir(run_obj.case.name, run_obj)
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
    vcf = api.assets(category='vcf-clinical', run_id=run_obj.id).one()
    sv_vcf = api.assets(category='vcf-clinical-sv', run_id=run_obj.id).first()
    research_vcf = api.assets(category='vcf-research', run_id=run_obj.id).one()
    sv_researchvcf = api.assets(category='vcf-research-sv', run_id=run_obj.id).first()
    sampleinfo = api.assets(category='sampleinfo', run_id=run_obj.id).one()

    qc_ped = api.assets(category='qcpedigree', run_id=run_obj.id).one()
    with open(qc_ped.path, 'r') as in_handle:
        content = yaml.load(in_handle)
        qc_samples = content[family]
    bams = api.assets(category='bam', run_id=run_obj.id)
    samples = []
    for bam in bams:
        sample_data = parse_sample(qc_samples[bam.sample.name], bam.path)
        samples.append(sample_data)

    default_panels = set()
    for sample in qc_samples.values():
        for panel in sample['Clinical_db']:
            default_panels.add(panel)
    default_panels = list(default_panels)

    with open(sampleinfo.path, 'r') as in_handle:
        si_data = yaml.load(in_handle)
        si_root = si_data[family]

    rank_model = (si_root[family]['Program']['RankVariants']['RankModel']
                         ['Version'])
    genome_build = (si_root[family]['HumanGenomeBuild']['Source'] +
                    si_root[family]['HumanGenomeBuild']['Version'])

    # gene panels
    gene_list = si_root[family]['VCFParser']['SelectFile']['Path']
    panels = si_root[family]['VCFParser']['SelectFile']['Database'].values()
    gene_panels = [{
        'id': panel['Acronym'].strip(),
        'date': panel['Date'],
        'version': panel['Version'].strip(),
        'name': panel['CompleteName'].strip(),
    } for panel in panels]

    data = {
        'vcf': vcf.path,
        'institute': customer,
        'family': family,
        'sv_vcf': sv_vcf.path,
        'samples': samples,
        'default_panels': default_panels,
        'rank_model_version': rank_model,
        'analysis_date': si_root[family]['AnalysisDate'],
        'human_genome_build': genome_build,
        'research_vcf': research_vcf.path,
        'research_sv_vcf': sv_researchvcf.path,
        'gene_list': {
            'path': gene_list,
            'panels': gene_panels
        },
    }
    return data


def parse_sample(sample_data, bam_path):
    """Parse out sample information from QC pedigree block."""
    data = {
        'id': sample_data['Individual ID'],
        'name': sample_data['display_name'][0],
        'sex': SEX_MAP.get(sample_data['Sex'], 'unknown'),
        'phenotype': PHENOTYPE_MAP.get(sample_data['Phenotype'], 'unknown'),
        'analysis_type': sample_data['Sequencing_type'][0].lower(),
        'capture_kit': sample_data.get('Capture_kit', [None])[0],
        'bam_path': bam_path,
        'father': sample_data.get('Paternal ID'),
        'mother': sample_data.get('Maternal ID'),
    }
    return data
