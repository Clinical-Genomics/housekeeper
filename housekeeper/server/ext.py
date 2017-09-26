# -*- coding: utf-8 -*-
from flask_alchy import Alchy

from housekeeper.store import BaseHandler, models


class HousekeeperAlchy(Alchy, BaseHandler):
    pass


store = HousekeeperAlchy(Model=models.Model)
