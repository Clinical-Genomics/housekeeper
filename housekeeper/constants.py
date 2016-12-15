# -*- coding: utf-8 -*-
from datetime import timedelta

PIPELINES = ('mip',)
# three months before clean up by default
TIME_TO_CLEANUP = timedelta(days=(30 * 3))
ARCHIVE_TYPES = ('data', 'result', 'meta')
EXTRA_STATUSES = ['coverage', 'frequency', 'genotype', 'visualizer',
                  'rawdata', 'qc']
