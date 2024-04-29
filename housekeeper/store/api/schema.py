"""
Schema definitions
"""

import marshmallow as ma


class BaseSchema(ma.Schema):
    """
    Base class for marshmallow schemas
    """

    SKIP_VALUES = set([None])

    @ma.post_dump
    def remove_skip_values(self, data):
        """Remove values that are null in db"""
        return {key: value for key, value in data.items() if value not in self.SKIP_VALUES}


class TagSchema(ma.Schema):
    """
    Tag schema definition
    """

    id = ma.fields.Int()
    name = ma.fields.Str(required=True, error_messages={"required": "Tag name is required."})
    category = ma.fields.Str()
    created_at = ma.fields.DateTime()


class FileSchema(ma.Schema):
    """
    File schema definition
    """

    id = ma.fields.Int()
    path = ma.fields.Str(required=True, error_messages={"required": "File path is required."})
    full_path = ma.fields.Str(
        required=True, error_messages={"required": "Full file path is required."}
    )
    archive = ma.fields.Boolean(default=False)
    tags = ma.fields.List(ma.fields.Nested(TagSchema), required=True)


class InputFileSchema(ma.Schema):
    """
    File input schema definition

    This is used for files that are add via json in the CLI
    """

    path = ma.fields.Str(required=True, error_messages={"required": "File path is required."})
    bundle = ma.fields.Str(required=True, error_messages={"required": "Bundle name is required."})
    archive = ma.fields.Boolean(default=False)
    tags = ma.fields.List(ma.fields.Str, required=False)


class VersionSchema(ma.Schema):
    """
    Bundle schema definition
    """

    id = ma.fields.Int()
    created_at = ma.fields.DateTime(
        required=True, error_messages={"required": "Bundle date is required."}
    )
    expires_at = ma.fields.DateTime()
    included_at = ma.fields.DateTime()
    removed_at = ma.fields.DateTime()
    archived_at = ma.fields.DateTime()
    archived_path = ma.fields.Str()
    archived_checksum = ma.fields.Str()
    bundle_id = ma.fields.Int()
    files = ma.fields.List(ma.fields.Nested(FileSchema), required=True)


class InputVersionSchema(ma.Schema):
    """
    Bundle schema definition
    """

    created_at = ma.fields.Str(
        required=True, error_messages={"required": "Bundle date is required."}
    )
    expires_at = ma.fields.Str()
    included_at = ma.fields.Str()
    removed_at = ma.fields.Str()
    archived_at = ma.fields.Str()
    archived_path = ma.fields.Str()
    archived_checksum = ma.fields.Str()
    bundle_name = ma.fields.Str(required=True)
    files = ma.fields.List(ma.fields.Str(), required=False)


class BundleSchema(ma.Schema):
    """
    Bundle schema definition
    """

    id = ma.fields.Int()
    name = ma.fields.Str(required=True, error_messages={"required": "Bundle name is required."})
    created_at = ma.fields.DateTime(
        required=True, error_messages={"required": "Bundle date is required."}
    )
    files = ma.fields.List(ma.fields.Nested(FileSchema), required=True)
    versions = ma.fields.List(ma.fields.Nested(VersionSchema), required=True)


class InputBundleSchema(ma.Schema):
    """
    Bundle input schema definition

    Used when adding bundle via CLI
    """

    name = ma.fields.Str(required=True, error_messages={"required": "Bundle name is required."})
    created_at = ma.fields.Str(
        required=True, error_messages={"required": "Bundle date is required."}
    )
    expires_at = ma.fields.Str(required=False)
    files = ma.fields.List(ma.fields.Str, required=False)
