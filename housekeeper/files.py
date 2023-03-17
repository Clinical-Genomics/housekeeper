"""Functions for dealing with files"""

import json
import logging
from json.decoder import JSONDecodeError

import click
from marshmallow.exceptions import ValidationError

from housekeeper.store.api import schema as schemas

LOG = logging.getLogger(__name__)


def load_json(json_str: str) -> dict:
    """Load a json string"""
    LOG.info("Loading json information")
    try:
        data = json.loads(json_str)
    except JSONDecodeError as err:
        LOG.warning("Something wrong in json string")
        LOG.error(err)
        raise click.Abort
    LOG.info("Succesfull loading of JSON")
    return data


def validate_input(data: dict, input_type: str):
    """Validate input with the marshmallow schemas"""
    valid_schemas = {
        "bundle": schemas.InputBundleSchema(),
        "file": schemas.InputFileSchema(),
        "version": schemas.InputVersionSchema(),
    }
    schema = valid_schemas.get(input_type)
    if schema is None:
        LOG.warning("Invalid input type %s", input_type)
        raise ValueError()

    LOG.info("Validating bundle schema")

    formatted_data = schema.dump(data)
    try:
        LOG.info("Validate marshmallow schema")
        schema.load(formatted_data)
    except ValidationError as err:
        LOG.warning("Input data does not follow the models")
        LOG.error(err)
        raise click.Abort
    LOG.info("Input looks fine")
