"""Module for including files via CLI"""
import datetime as dt
import logging

import click

from housekeeper.exc import VersionIncludedError
from housekeeper.include import include_version

LOG = logging.getLogger(__name__)


@click.command()
@click.option("-v", "--version", type=int, help="version id of the bundle version")
@click.argument("bundle_name", required=False)
@click.pass_context
def include(context: click.Context, bundle_name: str, version: int):
    """Include a bundle of files into the internal space.

    Use bundle name if you simply want to include the latest version.
    """
    LOG.info("Running include")
    store = context.obj["store"]
    if version:
        LOG.info("Use version %s", version)
        version_obj = store.Version.get(version)
        if version_obj is None:
            LOG.warning("version not found")
    else:
        if not bundle_name:
            LOG.warning("Please specify bundle or version")
            return

        bundle_obj = store.bundle(bundle_name)
        if bundle_obj is None:
            LOG.warning("bundle %s not found", bundle_name)
        if len(bundle_obj.versions) == 0:
            LOG.error("Could not find any versions for bundle %s", bundle_name)
            raise click.Abort
        version_obj = bundle_obj.versions[0]

    try:
        include_version(context.obj["root"], version_obj)
    except VersionIncludedError as error:
        click.echo(click.style(error.message, fg="red"))
        context.abort()

    version_obj.included_at = dt.datetime.now()
    store.commit()
    click.echo(click.style("included all files!", fg="green"))
