# -*- coding: utf-8 -*-
"""This is a core module for the Store API"""

import logging
from pathlib import Path

from housekeeper.store.crud.create import CreateHandler
from housekeeper.store.crud.read import ReadHandler
from housekeeper.store.crud.update import UpdateHandler
from housekeeper.store.database import get_session
from housekeeper.store.models import File, Version

LOG = logging.getLogger(__name__)


class Store(CreateHandler, ReadHandler, UpdateHandler):
    """
    Handles interactions with the database in the context when a temporary
    database connection is needed, e.g., a command line interface.
    """

    def __init__(self, root: str):
        self.session = get_session()
        ReadHandler(self.session)
        CreateHandler(self.session)
        UpdateHandler(self.session)

        LOG.debug("Initializing Store")
        File.app_root = Path(root)
        Version.app_root = Path(root)

        super().__init__(self.session)
