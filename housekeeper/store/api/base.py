"""This module defines a BaseHandler class holding different models"""

from typing import Type
from housekeeper.store.models import Bundle, File, Version, Tag
from alchy import ModelBase, Query


class BaseHandler:
    """This is a base class holding different models"""

    Bundle: Type[ModelBase] = Bundle
    Version: Type[ModelBase] = Version
    File: Type[ModelBase] = File
    Tag: Type[ModelBase] = Tag
