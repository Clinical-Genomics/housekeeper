# -*- coding: utf-8 -*-
from housekeeper.store import Analysis


def test_add_mip(invoke_cli, mip_output, setup_tmp):
    # GIVEN some MIP analysis output
    assert Analysis.query.first() is None
    # WHEN adding a MIP analysis on the command line
    config = mip_output.joinpath('cust003/16074/genomes/16074/16074_config.yaml')
    result = invoke_cli(['-d', setup_tmp['uri'], 'add', 'mip', config])
    # THEN it should add the analysis and files to the database
    assert result.exit_code == 0
    assert Analysis.query.first().name == 'cust003-16074'
