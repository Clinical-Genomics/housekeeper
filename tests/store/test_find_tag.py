"""Tests for finding tags in store."""
from pathlib import Path
from typing import List

from housekeeper.store import Store
from housekeeper.store.models import Tag, File


def test_tag_with_tag_name(populated_store: Store, sample_tag_name: str):
    """Test fetching a tag from database given a tag name."""
    # GIVEN a populated store and a tag name

    # WHEN retrieving a tag from Store
    test_tag = populated_store.get_tag(tag_name=sample_tag_name)

    # THEN a tag should be returned
    assert isinstance(test_tag, Tag)

    # THEN the tag should have the tag name gotten as parameter
    assert test_tag.name == sample_tag_name


def test_tag_without_tag_name(populated_store: Store):
    """Test fetching a tag from database without specifying a tag name returns None."""
    # GIVEN a populated store

    # WHEN retrieving a tag from Store
    test_tag = populated_store.get_tag()

    # THEN a tag should be returned
    assert test_tag is None


def test_get_archived_files(
    archived_file: Path, non_archived_file:Path, populated_store: Store, sample_id: str, spring_tag
):
    """Tests fetching all spring files in a given bundle that are archived."""
    # GIVEN a bundle with two files, where one is archive and one is not

    # WHEN asking for all archived files
    archived_files: List[Path] = [Path(file.path) for file in populated_store.get_archived_files(
        bundle_name=sample_id, tags=[spring_tag]
    )]

    # THEN only one should be returned
    assert archived_file in archived_files
    assert non_archived_file not in archived_files

def test_get_non_archived_files(
    archived_file: Path, non_archived_file:Path, populated_store: Store, sample_id: str, spring_tag
):
    """Tests fetching all spring files in a given bundle that are not archived."""
    # GIVEN a bundle with two files, where one is archive and one is not

    # WHEN asking for all non-archived files
    archived_files: List[Path] = [Path(file.path) for file in populated_store.get_non_archived_files(
        bundle_name=sample_id, tags=[spring_tag]
    )]

    # THEN only one should be returned
    assert archived_file not in archived_files
    assert non_archived_file in archived_files