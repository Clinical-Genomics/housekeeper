"""
This module handles updating entries in the store/database
"""
import datetime as dt
import logging
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Query, Session

from housekeeper.store.filters.bundle_filters import BundleFilters, apply_bundle_filter
from housekeeper.store.filters.file_filters import FileFilter, apply_file_filter
from housekeeper.store.filters.file_tags_filters import (
    FileJoinFilter,
    apply_file_join_filter,
)
from housekeeper.store.filters.version_bundle_filters import (
    VersionBundleFilters,
    apply_version_bundle_filter,
)
from housekeeper.store.filters.version_filters import (
    VersionFilter,
    apply_version_filter,
)
from housekeeper.store.models import Bundle, File, Tag, Version
from housekeeper.store.filters.tag_filters import TagFilter, apply_tag_filter

from .base import BaseHandler

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler):
    """Handler for updating entries in the database."""
    def __init__(self, session: Session):
        super().__init__(session=session)
    def set_archive_time_stamps(self):
        pass