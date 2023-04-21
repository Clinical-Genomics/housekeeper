# -*- coding: utf-8 -*-
"""This is a core module for the Store API"""

import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from housekeeper.store.models import Model
from housekeeper.store.api.add import AddHandler
from housekeeper.store.api.find import FindHandler

LOG = logging.getLogger(__name__)


class CoreHandler(FindHandler, AddHandler):
    """Aggregating class for the store api handlers"""

    def __init__(self, session):
        FindHandler(session=session)
        AddHandler(session=session)


class Store(CoreHandler):

    """
    Handles interactions with the database in the context when a temporary
    database connection is needed, e.g. a command line interface.

    Args:
        uri (str): SQLAlchemy database connection str
    """

    def __init__(self, uri: str, root: str):
        self.engine = create_engine(uri)
        session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(session_factory)

        LOG.debug("Initializing Store")
        self.File.app_root = Path(root)
        self.Version.app_root = Path(root)

        super().__init__(self.session)

    def create_all(self):
        """Create all tables in the database."""
        Model.metadata.create_all(bind=self.session.get_bind())

    def drop_all(self):
        """Drop all tables in the database."""
        Model.metadata.drop_all(bind=self.session.get_bind())
