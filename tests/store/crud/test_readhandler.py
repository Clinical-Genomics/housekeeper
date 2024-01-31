"""Tests for finding tags in store."""

import datetime
from datetime import timedelta
from pathlib import Path

import pytest

from housekeeper.store.models import Archive, File, Tag
from housekeeper.store.store import Store


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


def test_get_files_before(populated_store, bundle_data_old, time_stamp_now):
    """
    Test return all files when two bundles are added and all files are older.
    """
    # GIVEN a populated store
    store: Store = populated_store
    starting_nr_of_files: int = len(store.get_files_before(before_date=time_stamp_now))

    # GIVEN two new files
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.session.add(bundle_old_obj)
    store.session.commit()

    # WHEN fetching all files in the database
    files = store.get_files_before(before_date=time_stamp_now)

    # THEN two more files should be returned
    assert len(files) == starting_nr_of_files + 2


def test_get_past_files(populated_store, bundle_data_old, timestamp, old_timestamp):
    """
    test fetch files where not all files are older than before date.
    """
    store: Store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.session.add(bundle_old_obj)
    store.session.commit()

    # WHEN fetching all files before the oldest date
    date = old_timestamp + timedelta(days=10)
    assert old_timestamp < date < timestamp
    files: list[File] = store.get_files_before(before_date=date)

    # THEN a list of Files is returned
    assert isinstance(files[0], File)

    # THEN assert only files from the old bundle was found
    assert len(files) == 2


def test_get_no_get_files_before_oldest(populated_store, bundle_data_old, old_timestamp, timestamp):
    """
    Test get files where no files are older than before date.
    """
    store: Store = populated_store
    # GIVEN a store with two bundles and two files in each bundle
    bundle_old_obj, _ = store.add_bundle(data=bundle_data_old)
    store.session.add(bundle_old_obj)
    store.session.commit()

    # WHEN fetching all files before the oldest date
    date = old_timestamp - timedelta(days=10)
    assert date < old_timestamp < timestamp
    files: list[File] = store.get_files_before(before_date=date)

    # THEN assert no files where that old
    assert len(files) == 0


def test_get_archived_files_for_bundle(
    archived_file: Path,
    non_archived_file: Path,
    populated_store: Store,
    sample_id: str,
    spring_tag: str,
):
    """Tests fetching all archive SPRING files in a given bundle."""
    # GIVEN a bundle with two files, where one is archive and one is not

    # WHEN asking for all archived files
    archived_files: list[Path] = [
        Path(file.path)
        for file in populated_store.get_archived_files_for_bundle(
            bundle_name=sample_id, tags=[spring_tag]
        )
    ]

    # THEN only one should be returned
    assert archived_file in archived_files
    assert non_archived_file not in archived_files


def test_get_non_archived_files_for_bundle(
    archived_file: Path,
    non_archived_file: Path,
    populated_store: Store,
    sample_id: str,
    spring_tag: str,
):
    """Tests getting all non-archive SPRING files in a given bundle."""
    # GIVEN a bundle with two files, where one is archive and one is not

    # WHEN asking for all non-archived files
    archived_files: list[Path] = [
        Path(file.path)
        for file in populated_store.get_non_archived_files_for_bundle(
            bundle_name=sample_id, tags=[spring_tag]
        )
    ]

    # THEN only one should be returned
    assert archived_file not in archived_files
    assert non_archived_file in archived_files


def test_get_bundle_name_from_file_path(
    populated_store: Store, sample_id: str, spring_file_1: Path
):
    """Test that the bundle name is fetched correctly from a file path."""
    # GIVEN a store containing a spring file related to sample ACC123456A1

    # WHEN getting the bundle name for the file
    bundle_name: str = populated_store.get_bundle_name_from_file_path(spring_file_1.as_posix())

    # THEN the bundle name should be the sample name
    assert bundle_name == sample_id


@pytest.mark.parametrize("limit", [None, 0])
def test_get_non_archived_files(populated_store: Store, spring_tag: str, limit: int | None):
    """Test that getting all non-archived spring files from the store
    returns all files fulfilling said condition."""
    # GIVEN a populated store containing SPRING and non-SPRING entries
    all_files: list[File] = populated_store.get_files().all()
    assert all_files

    # WHEN retrieving all non archived spring files
    non_archived_spring_files: list[File] = populated_store.get_non_archived_files(
        tag_names=[spring_tag], limit=limit
    )

    # WHEN no limit was set
    if limit is None:
        # THEN entries should be returned
        assert non_archived_spring_files

        # THEN all files with archives and the SPRING tag should be returned
        for file in all_files:
            if file not in non_archived_spring_files:
                assert file.archive or spring_tag not in [tag.name for tag in file.tags]
            else:
                assert not file.archive
                assert spring_tag in [tag.name for tag in file.tags]
                assert file in non_archived_spring_files

    # WHEN a limit is set to not fetch any files
    else:
        # THEN no files should be returned
        assert not non_archived_spring_files


def test_get_ongoing_archiving_tasks(
    archive: Archive, archiving_task_id: int, populated_store: Store
):
    """Tests returning unfinished archiving tasks ids."""
    # GIVEN a populated store with one ongoing archiving task
    archive.archiving_task_id = archiving_task_id
    archive.archived_at = None

    # WHEN getting ongoing archiving tasks
    ongoing_task_ids: set[int] = set(
        archive_entry.archiving_task_id for archive_entry in populated_store.get_ongoing_archivals()
    )

    # THEN the set should include the initial archiving task id
    assert archiving_task_id in ongoing_task_ids


def test_get_ongoing_retrieval_tasks(
    archive: Archive, retrieval_task_id: int, populated_store: Store
):
    """Tests the returning of ongoing retrieval tasks."""
    # GIVEN a populated store with one ongoing retrieval task
    archive.retrieval_task_id = retrieval_task_id
    archive.retrieved_at = None

    # WHEN getting ongoing retrieval tasks
    ongoing_task_ids: set[int] = set(
        archive_entry.retrieval_task_id
        for archive_entry in populated_store.get_ongoing_retrievals()
    )

    # THEN the set should include the initial retrieval task id
    assert retrieval_task_id in ongoing_task_ids


def test_get_archive_entries_by_archiving_id(
    archive: Archive, archiving_task_id: int, populated_store: Store
):
    """Tests that get_archives returns archive entries with the given archiving task id."""

    # GIVEN a populated store with an archive entry

    # WHEN getting entries with the matching archiving task id
    archives: list[Archive] = populated_store.get_archives(archival_task_id=archiving_task_id)

    # THEN the matching entry should have been returned
    assert archive in archives


def test_get_archive_entries_by_retrieval_id(retrieval_task_id: int, populated_store: Store):
    """Tests that get_archives returns archive entries with the given archiving task id."""

    # GIVEN a populated store with an archive entry

    # WHEN getting entries with the matching retrieval task id
    archives: list[Archive] = populated_store.get_archives(retrieval_task_id=retrieval_task_id)

    # THEN an Archive entry should be returned
    assert archives

    # THEN all returned entries should have the specified retrieval task id
    for archive in archives:
        assert archive.retrieval_task_id == retrieval_task_id


def test_archives_not_returned_via_archiving_id(archiving_task_id: int, populated_store: Store):
    """Tests that only archives with matching archiving task ids are returned."""

    # GIVEN a store with multiple archive entries, out of which only one has the provided archiving task id

    # WHEN fetching all archives
    all_archives: list[Archive] = populated_store.get_archives()

    # WHEN fetching all archives with a specified archiving task id
    selected_archives: list[Archive] | None = populated_store.get_archives(
        archival_task_id=archiving_task_id
    )

    # THEN only archives with the matching retrieval task id is returned
    assert len(all_archives) > len(selected_archives)
    for archive in all_archives:
        if archive.archiving_task_id == archiving_task_id:
            assert archive in selected_archives
        else:
            assert archive not in selected_archives


def test_archives_not_returned_via_retrieval_id(retrieval_task_id: int, populated_store: Store):
    """Tests that only archives with matching retrieval task ids are returned."""

    # GIVEN a store with multiple archive entries, out of which only one has the provided retrieval task id

    # WHEN fetching all archives
    all_archives: list[Archive] = populated_store.get_archives()

    # WHEN fetching all archives with a specified retrieval task id
    selected_archives: list[Archive] | None = populated_store.get_archives(
        retrieval_task_id=retrieval_task_id
    )

    # THEN only archives with the matching retrieval task id is returned
    assert len(all_archives) > len(selected_archives)
    for archive in all_archives:
        if archive.retrieval_task_id == retrieval_task_id:
            assert archive in selected_archives
        else:
            assert archive not in selected_archives


@pytest.mark.parametrize(
    "retrieved_at, tags, should_be_returned",
    [
        (datetime.datetime(year=2023, month=12, day=12), [], False),
        (datetime.datetime(year=2023, month=1, day=1), [], True),
        (datetime.datetime(year=2023, month=1, day=1), ["spring"], True),
        (datetime.datetime(year=2023, month=1, day=1), ["fastq"], False),
        (None, [], False),
    ],
    ids=[
        "Newly retrieved file",
        "Old retrieved file",
        "Old retrieved Spring file",
        "Old retrieved Fastq file",
        "Not retrieved file",
    ],
)
def test_filter_by_retrieved_before(
    archive: Archive,
    retrieval_task_id: int,
    populated_store: Store,
    retrieved_at: datetime,
    tags: list[str],
    should_be_returned: bool,
):
    """Tests filtering archives on only those retrieved before a given date or tagged with the given tags."""
    # GIVEN a store with an archive with the given retrieval task id and which was retrieved at the given time
    archive.retrieval_task_id = retrieval_task_id
    archive.retrieved_at = retrieved_at

    # GIVEN that we want only files that were retrieved before 2023-06-06 and tagged with the provided tags
    date: datetime = datetime.datetime(year=2023, month=6, day=6)

    # WHEN filtering by when it was retrieved
    files_retrieved_before_date: list[File] = populated_store.get_files_retrieved_before(
        date=date, tag_names=tags
    )

    # THEN the archive is only returned if it was retrieved before date
    assert (archive.file in files_retrieved_before_date) == should_be_returned
