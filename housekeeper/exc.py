# -*- coding: utf-8 -*-


class HousekeeperError(Exception):

    def __init__(self, message):
        self.message = message


class VersionIncludedError(HousekeeperError):
    pass


class BundleValidationError(HousekeeperError):
    pass
