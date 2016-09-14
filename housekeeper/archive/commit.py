# -*- coding: utf-8 -*-
from datetime import datetime

from .core import compress_run


def archive(run_obj):
    """High level archive function for a run."""
    groups = compress_run(run_obj)
    for group in groups:
        setattr(run_obj, "{}_archive".format(group.id), group.out)
        setattr(run_obj, "{}_checksum".format(group.id), group.checksum)
    run_obj.archived_at = datetime.now()
