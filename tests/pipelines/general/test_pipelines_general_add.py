# -*- coding: utf-8 -*-
from datetime import datetime

from housekeeper.pipelines.general import add


def test_analysis():
    # GIVEN information on a new analysis
    pipeline = 'mip'
    version = 'v4.0.0'
    analyzed_at = datetime.now()
    # WHEN building a new analysis model
    new_run = add.analysis(pipeline, version, analyzed_at)
    # THEN it should return the analysis model with samples
    assert new_run.pipeline == pipeline
    assert len(new_run.samples) == 0
