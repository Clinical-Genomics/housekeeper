# -*- coding: utf-8 -*-
from __future__ import division
from housekeeper.pipelines.mip import collect


def test_total_mapped():
    # GIVEN the path to the samtools multiqc summary
    path = ("tests/fixtures/mip/cust003/16074/analysis/genomes/ADM1594A12/"
            "multiqc/multiqc_data/multiqc_samtools.txt")
    # WHEN calculating the overall mapping rate
    with open(path, 'r') as stream:
        mapped_reads = collect.total_mapped(stream)
    # THEN it should return the correct value
    assert mapped_reads['percentage'] == 891591355 / 920254494


def test_analysis(mip_output):
    # GIVEN a MIP analysis without alterations
    config = mip_output.joinpath('cust003/16074/genomes/16074/16074_config.yaml')
    mod_qcmetrics = mip_output.joinpath("cust003/16074/analysis/genomes/16074/"
                                        "16074_qcmetrics.mod.yaml")
    assert not mod_qcmetrics.exists()
    # WHEN collecting information/preparing it for housekeeper
    records = collect.analysis(config)
    # THEN it should produce the modded qc metrics file
    assert mod_qcmetrics.exists()
    assert records['case'].name == 'cust003-16074'
    assert len(records['run'].samples) == 1
