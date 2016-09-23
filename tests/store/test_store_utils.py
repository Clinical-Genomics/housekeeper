# -*- coding: utf-8 -*-
from housekeeper.store import utils


def test_build_date():
    # GIVEN a date string in the iso format
    date_str = '2015-02-19'
    # WHEN converting to a date object
    date_obj = utils.build_date(date_str)
    # THEN it should parse out the values
    assert date_obj.day == 19
    assert date_obj.month == 2
    assert date_obj.year == 2015
