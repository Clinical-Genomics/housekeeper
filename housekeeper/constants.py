# -*- coding: utf-8 -*-
from datetime import timedelta

PIPELINES = ('mip',)
ASSET_CATEGORIES = ('alignment', 'variants', 'logging', 'input')
# three months before archive by default
TIME_TO_ARCHIVE = timedelta(days=(30 * 3))
