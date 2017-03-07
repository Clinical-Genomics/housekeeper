# -*- coding: utf-8 -*-
import codecs
import logging
import os
import pkg_resources

import click
import coloredlogs
import yaml

log = logging.getLogger(__name__)


class EntryPointsCLI(click.MultiCommand):

    """Add subcommands dynamically to a CLI via entry points."""

    def _iter_commands(self):
        """Iterate over all subcommands as defined by the entry point."""
        return {entry_point.name: entry_point for entry_point in
                pkg_resources.iter_entry_points('housekeeper.subcommands.1')}

    def list_commands(self, ctx):
        """List the available commands."""
        commands = self._iter_commands()
        return commands.keys()

    def get_command(self, ctx, name):
        """Load one of the available commands."""
        commands = self._iter_commands()
        if name not in commands:
            click.echo("no such command: {}".format(name))
            ctx.abort()
        return commands[name].load()


def build_cli(title, Model):
    """Build base cli from scratch."""
    version = pkg_resources.get_distribution(title).version

    @click.group(cls=EntryPointsCLI)
    @click.option('-c', '--config', default="~/.{}.yaml".format(title),
                  type=click.Path(), help='path to config file')
    @click.option('-d', '--database', help='path/URI of the SQL database')
    @click.option('-r', '--root', type=click.Path(exists=True),
                  help='root dir for storing analyses')
    @click.option('-l', '--log-level', default='INFO')
    @click.version_option(version, prog_name=title)
    @click.pass_context
    def root(context, config, database, root, log_level):
        """Interact with CLI."""
        coloredlogs.install(level=log_level)
        log.debug("{}: version {}".format(title, version))

        # read in config file if it exists
        if os.path.exists(config):
            with codecs.open(config) as conf_handle:
                context.obj = yaml.load(conf_handle)
                context.obj['config'] = config
        else:
            context.obj = {}

        context.obj['database'] = (database if database else
                                   context.obj.get('database'))
        context.obj['root'] = root if root else context.obj.get('root')

    return root
