# -*- coding: utf-8 -*-
from path import path

from housekeeper.store import Metadata, Analysis


class AnalysisConflictError(Exception):
    pass


def analysis(manager, analysis_obj):
    """Store an analysis with files to the backend."""
    if Analysis.query.filter_by(name=analysis_obj.name).first():
        raise AnalysisConflictError("'{}' already added".format(analysis_obj.name))

    meta = Metadata.query.first()
    analysis_root = path(meta.analyses_root).joinpath(analysis_obj.name)
    if analysis_root.isdir():
        raise AnalysisConflictError("'{}' already exists".format(analysis_root))
    analysis_root.makedirs_p()

    for asset in analysis_obj.assets:
        original_path = path(asset.original_path)
        filename = original_path.basename()
        new_path = analysis_root.joinpath(filename)
        asset.path = new_path

    manager.add_commit(analysis_obj)

    try:
        for asset in analysis_obj.assets:
            path(asset.original_path).link(asset.path)
    except Exception:
        # clean up
        analysis_obj.delete()
