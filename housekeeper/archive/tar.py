# -*- coding: utf-8 -*-
import tarfile


def tar_files(out_file, files):
    """Group files into a tar archive."""
    with tarfile.open(out_file, mode='w:gz') as out_handle:
        for a_file in files:
            out_handle.add(a_file)


def untar_files(out_dir, tar_file):
    """Ungroup tar-ed filed into a directory."""
    with tarfile.open(tar_file, mode='r') as in_handle:
        in_handle.extractall(out_dir)
