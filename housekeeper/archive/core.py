# -*- coding: utf-8 -*-
"""Archive a run to PDC.

1. get the archives for the run
2. send to PDC function (magic happens)
3. update new table with information about archive
4. remove the archive files
5. update that the case is archived
"""
from datetime import datetime
import logging

from housekeeper.store import api

log = logging.getLogger(__name__)


def archive_run(run_obj):
    """Archive a run to PDC."""
    assert run_obj.compiled_at, "run not compiled yet"
    # fetch the archive assets
    assets = get_archiveassets(run_obj.id)
    # do PDC magic....
    # remove the archive assets
    for archive_type, asset in assets:
        log.debug("deleting: %s", asset.path)
        api.delete_asset(asset)
    run_obj.compiled_at = None
    # mark the case as archived
    run_obj.archived_at = datetime.now()


def get_archiveassets(run_id):
    """Get the archive assets for a run."""
    for archive_type in ("data", "result"):
        category = "archive-{}".format(archive_type)
        query = api.assets(run_id=run_id, category=category)
        asset = query.first()
        yield archive_type, asset
