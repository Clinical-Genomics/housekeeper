"""This module defines a BaseHandler class holding different models"""
from dataclasses import dataclass

from housekeeper.store import models


@dataclass
class BaseHandler:
    """This is a base class holding different models"""

    Bundle = models.Bundle
    Version = models.Version
    File = models.File
    Tag = models.Tag
