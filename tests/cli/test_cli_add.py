"""Tests for adding via CLI"""

from housekeeper.cli import add

# tests adding tags


def test_add_two_tags(populated_context, cli_runner):
    """Test to add a two tags to the database"""
    # GIVEN a context with a populated store, and a cli runner
    # GIVEN two new tags
    tag1 = "new-tag"
    tag2 = "other-tag"

    # WHEN trying to add two tags to the an existing file
    result = cli_runner.invoke(add.tag, [tag1, tag2], obj=populated_context)
    # THEN assert it has a zero exit status
    assert result.exit_code == 0
    # THEN check that the tags are logged
    assert tag1 in result.output
    # THEN check that the tags are logged
    assert tag2 in result.output


def test_add_existing_tag_existing_file(populated_context, cli_runner):
    """Test to add a existing tag to a file that exists"""
    # GIVEN a context with a populated store, and a cli runner
    store = populated_context["store"]
    # GIVEN a existing file id
    file_id = 1
    file_obj = store.File.get(file_id)
    # GIVEN that the new tag already exists for the file
    tag = file_obj.tags[0].name

    # WHEN trying to add the existing tag to the file
    result = cli_runner.invoke(
        add.tag, [tag, "-f", str(file_id)], obj=populated_context
    )
    # THEN assert it has a non zero exit status
    assert result.exit_code == 0
    # THEN check that it communicates that the tag existed
    assert f"{tag}: tag already added" in result.output


def test_add_tag_existing_file(populated_context, cli_runner):
    """Test to add a non existing tag to a file that exists"""
    # GIVEN a context with a populated store, and a cli runner
    store = populated_context["store"]
    # GIVEN a existing file id
    file_id = 1
    file_obj = store.File.get(file_id)
    assert file_obj
    # GIVEN a new tag
    tag = "new-tag"

    # WHEN trying to add a tag to the existing file
    result = cli_runner.invoke(
        add.tag, [tag, "-f", str(file_id)], obj=populated_context
    )
    # THEN assert it has a zero exit status
    assert result.exit_code == 0
    # THEN check that the tag is displayed in the output
    assert f"{tag}: tag created" in result.output


def test_add_tag_non_existing_file(populated_context, cli_runner):
    """Test to add a tag to a file that not exist"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a non existing file id
    missing_file_id = 42
    file_obj = store.File.get(missing_file_id)
    assert not file_obj

    # WHEN trying to add a tag to the non existing file
    result = cli_runner.invoke(
        add.tag, ["new-tag", "-f", str(missing_file_id)], obj=populated_context
    )
    # THEN assert it has a non zero exit status
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert "unable to find file" in result.output


# tests adding bundles


def test_add_existing_bundle(populated_context, cli_runner):
    """Test to add a bundle that exists"""
    # GIVEN a context with a populated store and a cli runner
    store = populated_context["store"]
    # GIVEN a existing bundle
    bundle_obj = store.Bundle.query.first()
    assert bundle_obj
    bundle_name = bundle_obj.name

    # WHEN trying to add a bundle that exists
    result = cli_runner.invoke(add.bundle, [bundle_name], obj=populated_context)

    # THEN assert it has a non zero exit status
    assert result.exit_code == 1
    # THEN check that the error message is displayed
    assert "bundle name already exists" in result.output


def test_add_bundle(base_context, cli_runner, case_id):
    """Test to add a new bundle"""
    # GIVEN a context with a empty store and a cli runner
    bundle_name = case_id

    # WHEN trying to add a bundle
    result = cli_runner.invoke(add.bundle, [bundle_name], obj=base_context)

    # THEN assert it succeded
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert "new bundle added" in result.output


# tests adding file to bundle


def test_add_file_non_existing_bundle(
    base_context, cli_runner, case_id, second_sample_vcf
):
    """Test to add a file to a non existing bundle"""
    # GIVEN a context with a empty store and a cli runner
    unknown_bundle_name = case_id

    # WHEN trying to add a bundle
    result = cli_runner.invoke(
        add.file_cmd, [unknown_bundle_name, str(second_sample_vcf)], obj=base_context
    )

    # THEN assert it fails
    assert result.exit_code == 1
    # THEN check that the proper information is displayed
    assert f"unknown bundle: {unknown_bundle_name}" in result.output


def test_add_file_existing_bundle(
    populated_context, cli_runner, case_id, second_sample_vcf
):
    """Test to add a file to a existing bundle"""
    # GIVEN a context with a populated store and a cli runner
    bundle_name = case_id

    # WHEN trying to add the file to a bundle
    result = cli_runner.invoke(
        add.file_cmd, [bundle_name, str(second_sample_vcf)], obj=populated_context
    )

    # THEN assert it succedes
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert "new file added" in result.output


def test_add_non_existing_bundle_file(populated_context, cli_runner, case_id):
    """Test to add a file that does not exist"""
    # GIVEN a context with a populated store and a cli runner
    bundle_name = case_id
    non_existing_file = "hello.mate"

    # WHEN trying to add a non existing file to a bundle
    result = cli_runner.invoke(
        add.file_cmd, [bundle_name, non_existing_file], obj=populated_context
    )

    # THEN assert it fails
    assert result.exit_code == 1
    # THEN check that the proper information is displayed
    assert f"File {non_existing_file} does not exist" in result.output
