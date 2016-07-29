# -*- coding: utf-8 -*-
from .base import build_cli
from housekeeper.store.models import Model

root = build_cli('housekeeper', Model=Model)
