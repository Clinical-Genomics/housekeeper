"""Tests foe adding files via CLI"""
import logging

from housekeeper.cli.add import file_cmd


def test_add_file_non_existing_bundle(
    base_context, cli_runner, case_id, second_sample_vcf, caplog
):
    """Test to add a file to a non existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a empty store and a cli runner
    unknown_bundle_name = case_id

    # WHEN trying to add a bundle
    result = cli_runner.invoke(
        file_cmd, [unknown_bundle_name, str(second_sample_vcf)], obj=base_context
    )

    # THEN assert it fails
    assert result.exit_code == 1
    # THEN check that the proper information is displayed
    assert f"unknown bundle: {unknown_bundle_name}" in caplog.text


def test_add_file_existing_bundle(
    populated_context, cli_runner, case_id, second_sample_vcf, caplog
):
    """Test to add a file to a existing bundle"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a context with a populated store and a cli runner
    bundle_name = case_id

    # WHEN trying to add the file to a bundle
    result = cli_runner.invoke(
        file_cmd, [bundle_name, str(second_sample_vcf)], obj=populated_context
    )

    # THEN assert it succedes
    assert result.exit_code == 0
    # THEN check that the proper information is displayed
    assert "new file added" in caplog.text
