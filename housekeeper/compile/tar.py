# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os
import tarfile


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def tar_files(out_file, root_dir, filenames):
    """Group files into a tar archive."""
    with cd(root_dir):
        with tarfile.open(out_file, mode='w:gz') as out_handle:
            for filename in filenames:
                out_handle.add(filename)


def untar_files(out_dir, tar_file):
    """Ungroup tar-ed filed into a directory."""
    with tarfile.open(tar_file, mode='r:*') as in_handle:
        in_handle.extractall(out_dir)
