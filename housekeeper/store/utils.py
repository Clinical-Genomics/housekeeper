# -*- coding: utf-8 -*-
from datetime import date as make_date
import logging

from path import Path

log = logging.getLogger(__name__)


def get_rundir(root_path, case_name, run=None):
    """Return path to run root dir."""
    case_root = Path(root_path).joinpath(case_name)
    if run:
        run_root = case_root.joinpath(run.analysis_date.isoformat())
        return run_root
    else:
        return case_root


def build_date(date_str):
    """Parse date out of string."""
    return make_date(*map(int, date_str.split('-')))
