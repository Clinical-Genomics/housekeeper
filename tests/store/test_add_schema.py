"""
Tests for store add functionality
"""
from housekeeper.store.api import schema


def test_schema_with_invalid_input(bundle_data_json):
    # GIVEN input data with missing name of the bundle
    del bundle_data_json["name"]
    # WHEN validating it against the schema
    errors = schema.BundleSchema().validate(bundle_data_json)
    # THEN it should report errors for the field
    assert len(errors) > 0
    assert "name" in errors
