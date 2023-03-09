"""Class with helper functions to use in tests"""

import datetime as dt
import json
from typing import Iterable, List

from housekeeper.constants import LOGLEVELS
from housekeeper.store import Store


class Helpers:
    """Hold small methods that might be helpful for the tests"""

    @staticmethod
    def count_iterable(iter_obj: Iterable) -> int:
        """Count the length of a iterable"""
        return sum(1 for item in iter_obj)

    @staticmethod
    def get_stdout(output: str) -> str:
        """Strip log messages from a string"""
        stripped = []
        # Strip logging lines
        for line in output.split("\n"):
            if any(log_level in line for log_level in LOGLEVELS):
                continue
            stripped.append(line)
        return "\n".join(stripped)

    @staticmethod
    def get_json(output: str) -> List:
        """Convert a string to json"""
        output = Helpers.get_stdout(output)
        return json.loads(output)

    @staticmethod
    def add_bundle(store: Store, bundle: dict) -> None:
        """Add and commit bundle to housekeeper store"""
        bundle_obj, _ = store.add_bundle(bundle)
        store.add_commit(bundle_obj)

    @staticmethod
    def create_bundle_data(case_id: str, sample_data: dict, family_data: dict, created_at: dt.datetime = None) -> dict:
        """
        Create a new bundle_data dictionary with the given parameters.

        :param case_id: The name of the bundle.
        :param sample_data: A dictionary with information about the sample file.
        :param family_data: A dictionary with information about the family file.
        :param created_at: The timestamp when the bundle was created (optional).
        :return: A dictionary representing the bundle data.
        """
        if created_at is None:
            created_at = dt.datetime.now()

        data = {
            "name": case_id,
            "created_at": created_at,
            "files": [
                {
                    "path": str(sample_data["file"]),
                    "archive": False,
                    "tags": sample_data["tags"],
                },
                {
                    "path": str(family_data["file"]),
                    "archive": True,
                    "tags": family_data["tags"],
                },
            ],
        }

        return data
