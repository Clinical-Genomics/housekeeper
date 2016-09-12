# -*- coding: utf-8 -*-


class AnalysisConflictError(Exception):
    pass


class MissingFileError(Exception):
    pass


class AnalysisNotFinishedError(Exception):
    pass


class UnsupportedVersionError(Exception):
    pass


class MalformattedPedigreeError(Exception):
    pass
