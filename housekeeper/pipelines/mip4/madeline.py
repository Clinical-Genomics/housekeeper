# -*- coding: utf-8 -*-
import codecs
import os.path
import subprocess
import shutil
from tempfile import NamedTemporaryFile, mkdtemp

from ped_parser import FamilyParser


class SinglePedigreeError(Exception):
    pass


class MadelineIncompatibleError(Exception):
    pass


def run(ped_stream, sample_map, exe):
    """Run Madeline and capture the output."""
    ped = FamilyParser(ped_stream, family_type='alt', cmms_check=False)
    external_individuals = external_ped(ped.individuals, sample_map)
    family_id = ped.families.keys()[0]
    ped.families[family_id].individuals = external_individuals

    madeline_exe = os.path.abspath(exe)
    output_dir = mkdtemp()
    output_prefix = "{}/madeline".format(output_dir)
    out_path = "{}.xml".format(output_prefix)

    if not any([ind.has_parents for ind in ped.individuals.values()]):
        raise MadelineIncompatibleError("Madeline needs connected individuals")

    madeline_ped_lines = list(ped.to_madeline())
    if len(madeline_ped_lines) == 2:
        raise SinglePedigreeError("can't generate pedigree with single"
                                  "individual")

    # write the input to a temp file
    with NamedTemporaryFile('r+w') as in_file:
        madeline_content = '\n'.join(madeline_ped_lines)
        in_file.write(madeline_content)
        in_file.flush()

        subprocess.call([madeline_exe, '--color', '--outputprefix',
                         output_prefix, in_file.name])

    with codecs.open(out_path, 'r') as output:
        svg_content = output.read()

    # strip away the script tag
    script_tag = ('<script type="text/javascript" xlink:href='
                  '"javascript/madeline.js"></script>')
    svg_content.replace(script_tag, '')

    shutil.rmtree(output_dir)
    return svg_content


def external_ped(ped_individuals, sample_map):
    """Convert and fill out 'ped' with external ids."""
    external_individuals = {}
    for individual_id, individual in ped_individuals.items():
        external_id = sample_map.get(individual_id)
        individual.individual_id = external_id
        individual.mother = sample_map.get(individual.mother, '0')
        individual.father = sample_map.get(individual.father, '0')
        # all individuals in the pedigree have been sequenced
        individual.consultand = 'Yes'
        external_individuals[external_id] = individual

    return external_individuals
