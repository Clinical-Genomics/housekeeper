# -*- coding: utf-8 -*-
import datetime as dt
import logging
from typing import List
from dateutil.parser import parse as parse_date
from pathlib import Path

import alchy

from housekeeper.store.api.add import AddHandler
from housekeeper.store.api.find import FindHandler
from housekeeper.store import models

log = logging.getLogger(__name__)




class CoreHandler(FindHandler, AddHandler):
    """Aggregating class for the store api handlers"""


class Store(alchy.Manager, CoreHandler):

    """
    Handles interactions with the database in the context when a temporary
    database connection is needed, e.g. a command line interface.

    Args:
        uri (str): SQLAlchemy database connection str
    """

    def __init__(self, uri: str, root: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=models.Model)
        self.File.app_root = Path(root)
        self.Version.app_root = Path(root)