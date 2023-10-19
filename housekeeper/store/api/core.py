# -*- coding: utf-8 -*-
"""This is a core module for the Store API"""

import logging
from pathlib import Path

from housekeeper.store.database import get_session
from housekeeper.store.api.handlers.update import UpdateHandler
from housekeeper.store.api.handlers.create import CreateHandler
from housekeeper.store.api.handlers.read import ReadHandler
from housekeeper.store.models import File, Version

LOG = logging.getLogger(__name__)


class CoreHandler(CreateHandler, ReadHandler, UpdateHandler):
    """Aggregating class for the store api handlers"""

    def __init__(self, session):
        ReadHandler(session)
        CreateHandler(session)
        UpdateHandler(session)


class Store(CoreHandler):

    """
    Handles interactions with the database in the context when a temporary
    database connection is needed, e.g. a command line interface.

    Args:
        uri (str): SQLAlchemy database connection str
    """

    def __init__(self, root: str):
        self.session = get_session()

        LOG.debug("Initializing Store")
        File.app_root = Path(root)
        Version.app_root = Path(root)

        super().__init__(self.session)
