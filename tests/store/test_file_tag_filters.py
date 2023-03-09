


from typing import List
from housekeeper.store.api.core import Store
from housekeeper.store.filters.file_tags_filters import filter_files_by_tags
from housekeeper.store.models import File


def test_filter_files_by_tags_returns_correct_files(populated_store: Store):
    """Test filtering files by tags."""

    # GIVEN a store with files
    file: File = populated_store._get_file_query().first()
    tag_names: List[str] = [tag.name for tag in file.tags]

    # WHEN filtering files by tags
    filtered_files_query = filter_files_by_tags(
        files_tags=populated_store._get_file_tag_query(),
        tags=tag_names,
    )

    filtered_files: List[File] = filtered_files_query.all()

    # THEN each file should have all the requested tags
    for file in filtered_files:
        assert all(
            tag.name in tag_names for tag in file.tags
        )

def test_filter_files_by_tags_returns_empty_list_when_no_files_match_tags(populated_store: Store):
    """Test filtering files by tags when no files match the given tags."""

    # GIVEN a store with files
    file: File = populated_store._get_file_query().first()

    # create a tag that does not exist in any files in the store
    tag_name = "nonexistent_tag"

    # WHEN filtering files by the nonexistent tag
    filtered_files_query = filter_files_by_tags(
        files_tags=populated_store._get_file_tag_query(),
        tags=[tag_name],
    )

    filtered_files: List[File] = filtered_files_query.all()

    # THEN the filtered files list should be empty
    assert len(filtered_files) == 0


def test_filter_files_by_tags_only_returns_files_that_match_all_tags(populated_store: Store):
    """Test filtering files by tags when some files match the tags but not all."""

    # GIVEN a store with files
    files_query = populated_store._get_file_query().join(File.tags)
    all_files = files_query.all()

    # select two tags that appear in some but not all files
    tag_names: List[str] = []
    for file in all_files:
        for tag in file.tags:
            if tag.name not in tag_names:
                tag_names.append(tag.name)
                if len(tag_names) == 2:
                    break
        if len(tag_names) == 2:
            break
    print(tag_names)
    # make sure there are some files that match both tags and some that match only one
    files_with_both_tags = []
    files_with_one_tag = []
    for file in all_files:
        file_tag_names = [tag.name for tag in file.tags]
        if set(tag_names).issubset(file_tag_names):
            files_with_both_tags.append(file)
        elif any(tag_name in file_tag_names for tag_name in tag_names):
            files_with_one_tag.append(file)

    assert len(files_with_both_tags) > 0
    assert len(files_with_one_tag) > 0

    # WHEN filtering files by the two tags
    filtered_files_query = filter_files_by_tags(
        files_tags=populated_store._get_file_tag_query(),
        tags=tag_names,
    )

    filtered_files: List[File] = filtered_files_query.all()

    # THEN the filtered files list should only include files that match all tags
    for file in filtered_files:
        assert all(tag.name in tag_names for tag in file.tags)

    # the number of filtered files should be less than the number of all files
    assert len(filtered_files) < len(all_files)