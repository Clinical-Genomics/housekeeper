# -*- coding: utf-8 -*-
import logging

import click
from path import Path

from housekeeper.store import api

log = logging.getLogger(__name__)


def migrate_root(manager, old_root, new_root, only_db=False):
    """Migrate root of analysis assets."""
    new_root = Path(new_root).abspath().normpath()
    log.debug("ensure parent of new root exists: %s", new_root.parent)
    new_root.parent.makedirs_p()
    if not only_db and new_root.exists():
        raise ValueError("new root can't exist")
    if not only_db:
        move_root(old_root, new_root)
    replace_paths(old_root, new_root)
    manager.commit()


def move_root(old_root, new_root):
    """Move the analysis assets from one directory to another."""
    Path(old_root).move(new_root)


def replace_paths(old_root, new_root):
    """Replace root paths for assets."""
    all_assets = api.assets()
    with click.progressbar(all_assets,
                           label='updating asset paths',
                           length=all_assets.count()) as bar:
        for asset in bar:
            new_path = asset.path.replace(old_root, new_root)
            log.debug("replacing path: %s -> %s", asset.path, new_path)
            assert Path(new_path).exists(), "can't find asset: {}".format(new_path)
            asset.path = new_path
