# -*- coding: utf-8 -*-
from housekeeper.compile import core


def test_checksum(pedigree):
    # GIVEN a file with checksum
    checksum = pedigree['checksum']
    path = pedigree['path']
    # WHEN calculating the checksum
    calculated_checksum = core.checksum(path)
    # THEN it should come up the same as expected
    assert calculated_checksum == checksum
