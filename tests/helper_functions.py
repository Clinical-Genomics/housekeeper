"""Class with helper functions to use in tests"""

import datetime as dt
import json
from typing import Iterable

from housekeeper.constants import LOGLEVELS
from housekeeper.store.models import Archive
from housekeeper.store.store import Store


class Helpers:
    """Hold small methods that might be helpful for the tests"""

    @staticmethod
    def add_bundle(store: Store, bundle: dict) -> None:
        """Add and commit bundle to housekeeper store"""
        bundle_obj, version = store.add_bundle(bundle)
        store.session.add(bundle_obj)
        store.session.add(version)
        store.session.commit()

    @staticmethod
    def add_archive(store: Store, file_id: int, archiving_task_id: int = 1234) -> Archive:
        """Adds an archive object to the database."""
        new_archive: Archive = store.create_archive(
            file_id=file_id, archiving_task_id=archiving_task_id
        )
        store.session.add(new_archive)
        store.session.commit()
        return new_archive

    @staticmethod
    def create_bundle_data(case_id: str, files: list[dict], created_at: dt.datetime = None) -> dict:
        """Create a new bundle_data dictionary with the given parameters."""

        if created_at is None:
            created_at = dt.datetime.now()

        files = [
            {"path": str(file_data["file"]), "archive": True, "tags": file_data["tags"]}
            for file_data in files
        ]

        data = {
            "name": case_id,
            "created_at": created_at,
            "files": files,
        }

        return data
