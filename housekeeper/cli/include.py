"""Module for including files via CLI"""

import datetime as dt
import logging

import click

from housekeeper.constants import ROOT
from housekeeper.exc import VersionIncludedError
from housekeeper.include import include_version
from housekeeper.store.store import Store

LOG = logging.getLogger(__name__)


@click.command()
@click.option("--version-id", type=int, help="version id of the bundle version")
@click.argument("bundle_name", required=False)
@click.pass_context
def include(context: click.Context, bundle_name: str, version_id: int):
    """Include a bundle of files into the internal space.

    Use bundle name if you simply want to include the latest version.
    """
    LOG.info("Running include")
    store: Store = context.obj["store"]
    if not (version_id or bundle_name):
        LOG.warning("Please use bundle name or version-id")
        raise click.Abort

    if version_id:
        LOG.info("Use version %s", version_id)
        version_obj = store.get_version_by_id(version_id=version_id)
        if version_obj is None:
            LOG.warning("version not found")
            raise click.Abort

    if bundle_name:
        bundle = store.get_bundle_by_name(bundle_name=bundle_name)
        if bundle is None:
            LOG.warning("bundle %s not found", bundle_name)
            raise click.Abort

        if len(bundle.versions) == 0:
            LOG.error("Could not find any versions for bundle %s", bundle_name)
            raise click.Abort

        LOG.info("Including latest version for %s", bundle_name)
        version_obj = bundle.versions[0]

    try:
        include_version(context.obj[ROOT], version_obj)
    except VersionIncludedError as error:
        LOG.warning(error.message)
        raise click.Abort

    version_obj.included_at = dt.datetime.now()
    store.session.commit()
    click.echo(click.style("included all files!", fg="green"))
