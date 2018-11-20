#!/usr/env/bin python

import os
import sys

import ruamel.yaml
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from housekeeper.store import Store, models


def main(argv):
    cases_yaml = 'scripts/correct_sv_rank_model_cases_info.yaml'
    uri = 'mysql+pymysql://devuser:userdev@localhost:3308/housekeeper2-dev'
    root = '/mnt/hds/proj/bioinfo/STAGE/bundles'
    old_root = '/mnt/hds/proj/bioinfo/bundles'

    store = Store(uri=uri, root=root)

    tag_name = 'bioit#197'
    tag_obj = store.tag(tag_name)
    if not tag_obj:
        tag_obj = store.new_tag(tag_name)

    with open(cases_yaml) as cases_file:
        cases = ruamel.yaml.safe_load(cases_file)

        for current_case in cases.keys():
            #if current_case != 'ableakita':
            #    continue
            for file_type in ('vcf', 'selected'):
                current_selected = Path(cases[current_case]['original_vcf_paths'][file_type].replace(old_root, root))
                correct_selected = Path(cases[current_case]['corrected_vcf_paths'][file_type].replace(old_root, root))
                bundle_date = cases[current_case]['bundle_date']

                # mv current file to $current_bioit#197
                current_selected_stem = str(current_selected).split('.')[0]
                display_file_type = f"{file_type}." if file_type == 'selected' else ''
                broken_selected = Path(f"{current_selected_stem}_bioit197.{display_file_type}vcf.gz")
                if not broken_selected.exists():
                    print(f"mv {current_selected} {broken_selected}")
                    current_selected.replace(broken_selected)
                else:
                    print(f"already exists: {broken_selected}")


                # hardlink correct file to HK
                if not current_selected.exists():
                    if not correct_selected.exists():
                        print(f"--- MISSING {correct_selected}")
                    else:
                        print(f"ln {correct_selected} {current_selected}")
                        os.link(correct_selected.resolve(), current_selected.resolve())
                else:
                    print(f"already exists: {current_selected}")

                # add broken file to HK
                version_objs = models.Version.query.join(models.Version.bundle).filter(models.Bundle.name == current_case, func.DATE(models.Version.created_at) == bundle_date).all()
                if len(version_objs) > 1:
                    print(f"--- SKIPPING {current_case}: too many versions")
                    continue
                version_obj = version_objs[0]

                try:
                    new_file = store.new_file(
                        path=str(Path(broken_selected).absolute()),
                        to_archive=True,
                        tags=[tag_obj]
                    )
                    new_file.version = version_obj
                    store.add_commit(new_file)
                    print(f"insert into file {broken_selected}")
                except IntegrityError:
                    store.session.rollback()
                    print(f"file already in db: {broken_selected}")
                sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
