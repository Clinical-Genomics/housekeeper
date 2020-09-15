"""Class with helper functions to use in tests"""

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
