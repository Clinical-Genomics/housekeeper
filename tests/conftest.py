# -*- coding: utf-8 -*-
import datetime

import pytest

from housekeeper.store import models, Store


@pytest.fixture
def version(tmpdir):
    file_path_1 = tmpdir.join('example.vcf.gz')
    file_path_1.write('content')
    file_path_2 = tmpdir.join('example2.txt')
    file_path_2.write('content')
    bundle_obj = models.Bundle(name='privatefox')
    version_obj = models.Version(created_at=datetime.datetime.now(), bundle=bundle_obj)
    version_obj.files.append(
        models.File(path=file_path_1, to_archive=True, tags=[models.Tag(name='vcf-gz')]),
    )
    version_obj.files.append(
        models.File(path=file_path_2, to_archive=False, tags=[models.Tag(name='tmp')])
    )
    return version_obj


@pytest.yield_fixture(scope='function')
def store(tmpdir):
    _store = Store(uri='sqlite://', root=str(tmpdir))
    _store.create_all()
    yield _store
    _store.drop_all()
