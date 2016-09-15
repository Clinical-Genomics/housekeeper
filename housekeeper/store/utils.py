# -*- coding: utf-8 -*-
from datetime import date as make_date
import logging

from .models import Metadata

log = logging.getLogger(__name__)


def get_rundir(case_name, run=None):
    """Return path to run root dir."""
    meta = Metadata.query.first()
    case_root = meta.root_path.joinpath(case_name)
    if run:
        run_root = case_root.joinpath(run.analysis_date.isoformat())
        return run_root
    else:
        return case_root


def build_date(date_str):
    """Parse date out of string."""
    return make_date(*map(int, date_str.split('-')))
