"""This module defines a BaseHandler class holding different models"""

from housekeeper.store import models


class BaseHandler:
    """This is a base class holding different models"""

    Bundle = models.Bundle
    Version = models.Version
    File = models.File
    Tag = models.Tag
