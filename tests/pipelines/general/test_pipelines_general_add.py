# -*- coding: utf-8 -*-
from datetime import datetime

from path import path

from housekeeper.pipelines.general import add


def test_asset(pedigree):
    # GIVEN a pedigree asset
    # WHEN preparing an asset model
    new_asset = add.asset(pedigree['path'], 'pedigree')
    # THEN it should return a model with checksum
    assert new_asset.original_path == path(pedigree['path']).abspath()
    assert new_asset.category == 'pedigree'


def test_analysis():
    # GIVEN information on a new analysis
    name = 'analysis_1'
    pipeline = 'mip'
    version = 'v3.0.0'
    analyzed_at = datetime.now()
    samples = ['sample_1']
    # WHEN building a new analysis model
    records = add.analysis(name, pipeline, version, analyzed_at,
                           samples=samples)
    # THEN it should return the analysis model with samples
    new_case = records['case']
    new_run = records['run']
    assert new_case.name == name
    assert new_run.pipeline == 'mip'
    assert len(new_run.samples) == 1
    assert new_run.samples[0].name == samples[0]
