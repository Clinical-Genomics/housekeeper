# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from .core import compress_run

log = logging.getLogger(__name__)


def archive_run(run_obj):
    """High level archive function for a run."""
    groups = compress_run(run_obj)
    for group in groups:
        log.info("compressed %s archive: %s", group.id, group.out)
        setattr(run_obj, "{}_archive".format(group.id), group.out)
        setattr(run_obj, "{}_checksum".format(group.id), group.checksum)
    run_obj.archived_at = datetime.now()
