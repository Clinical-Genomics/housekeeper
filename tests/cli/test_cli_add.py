# -*- coding: utf-8 -*-
from copy import deepcopy
import datetime

from pathlib import Path
import ruamel.yaml

from housekeeper.store import Store


def test_cli_add_file_to_bundle(store, store_url, tmpdir, invoke_cli, bundle_data, bundle_file_1, bundle_file_2):

    # add two versions of a bundle
    bundle_oldest = bundle_data
    bundle_latest = deepcopy(bundle_data)
    bundle_latest['created'] = datetime.datetime.now()
    for file_data in bundle_latest['files']:
        file_data['path'] = file_data['path'].replace('.vcf', '.2.vcf')
    with store.session.no_autoflush:
        for bundle in [bundle_oldest, bundle_latest]:
            bundle_obj, version_obj = store.add_bundle(bundle)
            store.add_commit(bundle_obj)
    store.session.flush()

    bundle_file_1 = bundle_file_1.replace('.vcf', '.3.vcf')
    bundle_file_2 = bundle_file_2.replace('.vcf', '.3.vcf')

    def_params = ['--database', store_url, '--root', tmpdir]
    
    # GIVEN you want to add a file to the latest version of the bundle
    bundle_name = bundle_data['name']
    result = invoke_cli(def_params + ['add', 'file', bundle_name, bundle_file_1])
    
    # WHEN a file is successsfully added
    assert result.exit_code == 0
    assert "new file added" in result.output

    # THEN the file should be found in the latest bundle
    result = invoke_cli(def_params + ['get', bundle_name])
    assert '.3.vcf' in result.output
    assert result.exit_code == 0
    
    # THEN the file should be found in the latest bundle
    result = invoke_cli(def_params + ['get', '--version', 2, bundle_name])
    assert '.3.vcf' in result.output
    assert result.exit_code == 0

    # THEN the file should not be found in the bundle before that
    result = invoke_cli(def_params + ['get', '--version', 1, bundle_name])
    assert '.3.vcf' not in result.output
    assert result.exit_code == 0
    
    # GIVEN you want to add a file to a specific version of the bundle
    version_1 = bundle_oldest['created']
    result = invoke_cli(def_params + ['add', 'file', '--version', version_1, bundle_name, bundle_file_2])

    # WHEN a file is successsfully added
    assert result.exit_code == 0
    assert "new file added" in result.output

    # THEN the file should be found in the latest bundle
    result = invoke_cli(def_params + ['get', bundle_name])
    assert '.3.vcf' in result.output
    assert result.exit_code == 0
    
    # THEN the file should be found in the latest bundle
    result = invoke_cli(def_params + ['get', '--version', 2, bundle_name])
    assert '.3.vcf' in result.output
    assert result.exit_code == 0

    # THEN the file should not be found in the bundle before that
    result = invoke_cli(def_params + ['get', '--version', 1, bundle_name])
    assert '.3.vcf' in result.output
    assert result.exit_code == 0
