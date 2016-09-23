# -*- coding: utf-8 -*-
import logging

from housekeeper.store import api, utils

log = logging.getLogger(__name__)


def run_orabort(context, case_name, date_str=None):
    """Get a run or abort the Click context."""
    run_date = utils.build_date(date_str) if date_str else None
    run_obj = api.runs(case_name, run_date=run_date).first()
    if run_obj is None:
        log.error("no analysis run found for case: %s", case_name)
        context.abort()
    else:
        return run_obj
