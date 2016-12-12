# -*- coding: utf-8 -*-


class HousekeeperError(Exception):

    def __init__(self, message=None):
        self.message = message


class AnalysisConflictError(HousekeeperError):
    pass


class MissingFileError(HousekeeperError):
    pass


class AnalysisNotFinishedError(HousekeeperError):
    pass


class UnsupportedVersionError(HousekeeperError):
    pass


class MalformattedPedigreeError(HousekeeperError):
    pass
