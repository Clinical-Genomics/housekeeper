# -*- coding: utf-8 -*-
from alchy import Manager

from .models import Model


def get_manager(uri):
    db = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return db
