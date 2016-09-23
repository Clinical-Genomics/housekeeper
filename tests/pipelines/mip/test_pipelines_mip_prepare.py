# -*- coding: utf-8 -*-
from __future__ import division
from housekeeper.pipelines.mip import prepare


def test_total_mapped():
    # GIVEN the path to the samtools multiqc summary
    path = ("tests/fixtures/mip/cust003/16074/analysis/genomes/ADM1594A12/"
            "multiqc/multiqc_data/multiqc_samtools.txt")
    # WHEN calculating the overall mapping rate
    with open(path, 'r') as stream:
        mapped_reads = prepare.total_mapped(stream)
    # THEN it should return the correct value
    assert mapped_reads['percentage'] == 891591355 / 920254494


def test_prepare_run(mip_output, segments):
    # GIVEN a MIP analysis without alterations
    mod_qcmetrics = mip_output.joinpath("cust003/16074/analysis/genomes/16074/"
                                        "16074_qcmetrics.mod.yaml")
    meta_suffix = "cust003/16074/analysis/genomes/meta.yaml"
    new_meta = mip_output.joinpath(meta_suffix)
    assert not mod_qcmetrics.exists()
    assert not new_meta.exists()
    # WHEN collecting information/preparing it for housekeeper
    prepare.prepare_run(segments)
    # THEN it should produce the modded qc metrics file
    assert mod_qcmetrics.exists()
    assert new_meta.exists()
