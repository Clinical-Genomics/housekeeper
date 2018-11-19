# -*- coding: utf-8 -*-
import datetime
import tempfile
import dateutil

import pytest
from pathlib import Path

from housekeeper import include
from housekeeper.store import models, Store


@pytest.fixture
def version(tmpdir):
    file_path_1 = tmpdir.join('example.vcf.gz')
    file_path_1.write('content')
    file_path_1_checksum = include.checksum(file_path_1)
    file_path_2 = tmpdir.join('example2.txt')
    file_path_2.write('content')
    bundle_obj = models.Bundle(name='privatefox')
    version_obj = models.Version(created_at=datetime.datetime.now(), bundle=bundle_obj)
    version_obj.files.append(
        models.File(path=file_path_1, to_archive=True, tags=[models.Tag(name='vcf-gz')],
            checksum=file_path_1_checksum),
    )
    version_obj.files.append(
        models.File(path=file_path_2, to_archive=False, tags=[models.Tag(name='tmp')])
    )
    return version_obj


@pytest.fixture(scope='function')
def bundle_data():
    data = {
        'name': 'sillyfish',
        'created': datetime.datetime.now(),
        'expires': datetime.datetime.now(),
        'files': [{
            'path': 'tests/fixtures/example.vcf',
            'archive': False,
            'tags': ['vcf', 'sample']
        }, {
            'path': 'tests/fixtures/family.vcf',
            'archive': True,
            'tags': ['vcf', 'family']
        }]
    }
    return data


@pytest.fixture(scope='function')
def bundle_data_old():
    data = {
        'name': 'angrybird',
        'created': dateutil.parser.parse('2018/01/01 00:00:00'),
        'expires': datetime.datetime.now(),
        'files': [{
            'path': 'tests/fixtures/example.2.vcf',
            'archive': False,
            'tags': ['vcf', 'sample']
        }, {
            'path': 'tests/fixtures/family.2.vcf',
            'archive': True,
            'tags': ['vcf', 'family']
        }]
    }
    return data


@pytest.fixture(scope='function')
def bundle_file_1():
    return 'tests/fixtures/example.vcf'


@pytest.fixture(scope='function')
def bundle_file_2():
    return 'tests/fixtures/family.vcf'


@pytest.fixture(scope='function')
def store_url(tmpdir):
    database_path = Path(tmpdir).joinpath('database.sqlite')
    return 'sqlite:///' + str(database_path)


@pytest.yield_fixture(scope='function')
def store(store_url, tmpdir):
    _store = Store(uri=store_url, root=str(tmpdir))
    _store.create_all()
    yield _store
#    _store.drop_all()
