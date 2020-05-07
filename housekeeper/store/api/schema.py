# -*- coding: utf-8 -*-
"""
Schema definitions
"""
from marshmallow import Schema, fields


class FileSchema(Schema):
    """
    File schema definition
    """

    path = fields.Str(
        required=True, error_messages={"required": "File path is required."}
    )
    archive = fields.Boolean(default=False)
    tags = fields.List(fields.Str(), required=True)


class BundleSchema(Schema):
    """
    Bundle schema definition
    """

    name = fields.Str(
        required=True, error_messages={"required": "Bundle name is required."}
    )
    created = fields.DateTime(
        required=True, error_messages={"required": "Bundle date is required."}
    )
    expires = fields.DateTime()
    files = fields.List(fields.Nested(FileSchema), required=True)
