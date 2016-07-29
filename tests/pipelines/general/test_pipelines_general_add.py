# -*- coding: utf-8 -*-
from datetime import datetime

from path import path

from housekeeper.pipelines.general import add


def test_checksum(pedigree):
    # GIVEN a file with checksum
    checksum = pedigree['checksum']
    path = pedigree['path']
    # WHEN calculating the checksum
    calculated_checksum = add.checksum(path)
    # THEN it should come up the same as expected
    assert calculated_checksum == checksum


def test_asset(pedigree):
    # GIVEN a pedigree asset
    # WHEN preparing an asset model
    new_asset = add.asset(pedigree['path'], 'pedigree')
    # THEN it should return a model with checksum
    assert new_asset.original_path == path(pedigree['path']).abspath()
    assert new_asset.checksum == pedigree['checksum']
    assert new_asset.category == 'pedigree'


def test_analysis():
    # GIVEN information on a new analysis
    name = 'analysis_1'
    pipeline = 'mip'
    version = 'v3.0.0'
    analyzed_at = datetime.now()
    samples = ['sample_1']
    # WHEN building a new analysis model
    new_analysis = add.analysis(name, pipeline, version, analyzed_at,
                                samples=samples)
    # THEN it should return the analysis model with samples
    assert new_analysis.name == name
    assert len(new_analysis.samples) == 1
    assert new_analysis.samples[0].name == samples[0]
