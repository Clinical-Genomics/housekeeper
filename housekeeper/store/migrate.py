# -*- coding: utf-8 -*-
import logging

from path import Path

from housekeeper.store import api

log = logging.getLogger(__name__)


def migrate_root(manager, old_root, new_root, only_db=False):
    """Migrate root of analysis assets."""
    new_root = Path(new_root).normpath()
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
    for asset in all_assets:
        new_path = asset.path.replace(old_root, new_root)
        log.dedug("replacing path: %s -> %s", asset.path, new_path)
        assert Path(new_path).exists(), "can't find asset: {}".format(new_path)
        asset.path = new_path
