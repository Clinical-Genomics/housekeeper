# -*- coding: utf-8 -*-
from housekeeper.pipelines.general import commit


def test_checksum(pedigree):
    # GIVEN a file with checksum
    checksum = pedigree['checksum']
    path = pedigree['path']
    # WHEN calculating the checksum
    calculated_checksum = commit.checksum(path)
    # THEN it should come up the same as expected
    assert calculated_checksum == checksum
