# -*- coding: utf-8 -*-
import logging
import hashlib

from path import path

from housekeeper.store import Analysis, Sample, Asset

log = logging.getLogger(__name__)

BLOCKSIZE = 65536


def analysis(name, pipeline, version, analyzed_at, samples=None):
    """Store information about a general analysis.

    This is the most low level implementation of how to store files from an
    analysis.
    """
    new_analysis = Analysis(name=name, pipeline=pipeline,
                            pipeline_version=version, analyzed_at=analyzed_at)
    for sample_id in (samples or []):
        new_analysis.samples.append(Sample(name=sample_id))
    return new_analysis


def asset(asset_path, category, for_archive=False):
    """Store an analysis file."""
    abs_path = path(asset_path).abspath()
    log.debug("calculate checksum for: %s", abs_path)
    sha1 = checksum(abs_path)
    new_asset = Asset(original_path=abs_path, checksum=sha1, category=category,
                      to_archive=for_archive)
    return new_asset


def checksum(path):
    """Calculcate checksum for a file."""
    hasher = hashlib.sha1()
    with open(path, 'rb') as stream:
        buf = stream.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = stream.read(BLOCKSIZE)
    return hasher.hexdigest()
