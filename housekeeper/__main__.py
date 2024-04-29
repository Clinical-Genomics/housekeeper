"""
housekeeper.__main__

The main entry point for the command line interface.

Invoke as `housekeeper` (if installed)
or `python -m housekeeper` (no install required).
"""

import sys

from housekeeper.cli.core import base

if __name__ == "__main__":
    # exit using whatever exit code the CLI returned
    sys.exit(base())
