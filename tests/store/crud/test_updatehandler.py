from datetime import datetime

from housekeeper import store
from housekeeper.store.models import Archive
from housekeeper.store.store import Store
from tests.helper_functions import Helpers


def test_update_archiving_time_stamp_new(archive: Archive, populated_store: store):
    """Tests updating the archived_at timestamp on a given archive when none is present."""
    # GIVEN an Archive with no archived_at timestamp
    assert not archive.archived_at

    # WHEN updating the timestamp
    populated_store.update_archiving_time_stamp(archive=archive)

    # THEN the timestamp should be updated
    assert archive.archived_at


def test_update_archiving_time_stamp_old(
    archive: Archive, old_timestamp: datetime, populated_store: store
):
    """Tests updating the archived_at timestamp on a given archive when there already is one."""
    # GIVEN an Archive with an old archived_at timestamp
    archive.archived_at = old_timestamp

    # WHEN updating the timestamp
    populated_store.update_archiving_time_stamp(archive=archive)

    # THEN the old timestamp should be kept
    assert archive.archived_at == old_timestamp


def test_update_retrieval_time_stamp_new(archive: Archive, populated_store: store):
    """Tests updating the retrieved_at timestamp on a given archive when none is present."""
    # GIVEN an Archive with no retrieved_at timestamp
    assert not archive.retrieved_at

    # WHEN updating the timestamp
    populated_store.update_retrieval_time_stamp(archive=archive)

    # THEN the timestamp should be updated
    assert archive.retrieved_at


def test_update_retrieval_time_stamp_old(
    archive: Archive, old_timestamp: datetime, populated_store: store
):
    """Tests updating the retrieved_at timestamp on a given archive when there already is one."""
    # GIVEN an Archive with an old retrieved_at timestamp
    archive.retrieved_at = old_timestamp

    # WHEN updating the timestamp
    populated_store.update_retrieval_time_stamp(archive=archive)

    # THEN the old timestamp should be kept
    assert archive.retrieved_at == old_timestamp


def test_update_finished_archival_task(
    archive: Archive, archiving_task_id: int, populated_store: Store
):
    """Tests updating all archives matching the given archiving task id."""
    # GIVEN a store with two archives with the same archiving task id
    second_archive: Archive = Helpers.add_archive(
        archiving_task_id=archiving_task_id, file_id=1, store=populated_store
    )

    # WHEN updating all archives with the given archiving task id
    populated_store.update_finished_archival_task(archiving_task_id=archiving_task_id)

    # THEN both archive should have their archived_at timestamp updated

    assert second_archive.archived_at
    assert archive.archived_at
    assert archive.archived_at.minute == second_archive.archived_at.minute


def test_update_finished_retrieval_task(
    archive: Archive, archiving_task_id, retrieval_task_id: int, populated_store: Store
):
    """Tests updating all archives matching the given retrieval task id."""
    # GIVEN a store with two archives with the same retrieval task id
    second_archive: Archive = Helpers.add_archive(
        archiving_task_id=archiving_task_id, file_id=1, store=populated_store
    )
    archive.retrieval_task_id = retrieval_task_id
    second_archive.retrieval_task_id = retrieval_task_id

    # WHEN updating all archives with the given retrieval task id
    populated_store.update_finished_retrieval_task(retrieval_task_id=retrieval_task_id)

    # THEN both archive should have their retrieved_at timestamp updated
    assert archive.retrieved_at
    assert second_archive.retrieved_at
    assert archive.retrieved_at.minute == second_archive.retrieved_at.minute


def test_update_retrieval_task_id(archive: Archive, retrieval_task_id: int, populated_store: store):
    """Tests updating the retrieved_at timestamp on a given archive when there already is one."""
    # GIVEN an Archive with no retrieval_task_id
    assert not archive.retrieval_task_id

    # WHEN updating the retrieval task id
    populated_store.update_retrieval_task_id(archive=archive, retrieval_task_id=retrieval_task_id)

    # THEN the retrieval task id should be set
    assert archive.retrieval_task_id == retrieval_task_id


def test_update_archiving_task_id(
    archive: Archive, new_archiving_task_id: int, populated_store: store
):
    """Tests updating the archiving_task_od on a given archive when there already is one.
    Necessary for retrieval and rearchiving."""
    # GIVEN an Archive with an old archiving_task_id
    assert archive.archiving_task_id != new_archiving_task_id

    # WHEN updating the archiving_task_id
    populated_store.update_archiving_task_id(
        archive=archive, archiving_task_id=new_archiving_task_id
    )

    # THEN the retrieval task id should be set
    assert archive.archiving_task_id == new_archiving_task_id
