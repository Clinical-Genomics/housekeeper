"""Class with helper functions to use in tests"""

import json
from typing import Iterable, List

from housekeeper.store import Store


class Helpers:
    """Hold small methods that might be helpful for the tests"""

    @staticmethod
    def count_iterable(iter_obj: Iterable) -> int:
        """Count the length of a iterable"""
        return sum(1 for item in iter_obj)

    @staticmethod
    def get_json(json_output: str) -> List:
        """Convert a string to json"""
        return json.loads(json_output)

    @staticmethod
    def add_bundle(store: Store, bundle: dict) -> None:
        """Add and commit bundle to housekeeper store"""
        bundle_obj, _ = store.add_bundle(bundle)
        store.add_commit(bundle_obj)
