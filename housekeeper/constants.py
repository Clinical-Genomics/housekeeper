"""Constants for housekeeper"""

from datetime import timedelta

LOGLEVELS = ["DEBUG", "INFO", "WARNING", "CRITICAL"]
PIPELINES = ("mip",)
# three months before clean up by default
TIME_TO_CLEANUP = timedelta(days=(30 * 3))
ARCHIVE_TYPES = ("data", "result", "meta", "archive")
EXTRA_STATUSES = ["coverage", "frequency", "genotype", "visualizer", "rawdata", "qc"]
ROOT: str = "root"
