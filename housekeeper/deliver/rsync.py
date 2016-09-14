# -*- coding: utf-8 -*-
"""
Rsync module based on:
https://gist.github.com/aerickson/1283442
"""
import logging
import re
import subprocess

log = logging.getLogger(__name__)


def sync_files(local_dir, remote_dir):
    """Sync a directory of files to a remote server."""
    # first dry-run to find out how many files to sync
    cmd = "rsync -az --stats --dry-run {} {}".format(local_dir, remote_dir)
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    remainder = proc.communicate()[0]
    groups = re.findall(r'Number of files: (\d+)', remainder)
    total_files = int(groups[0])
    log.info("number of files: %s", total_files)

    # now do the real rsync
    cmd = "rsync -avz --progress {} {}".format(local_dir, remote_dir)
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)

    while True:
        output = proc.stdout.readline()
        if 'to-check' in output:
            groups = re.findall(r'to-check=(\d+)/(\d+)', output)
            progress = (100 * (int(groups[0][1]) - int(groups[0][0]))) / total_files
            log.info("done: {}%".format(progress))
            if int(groups[0][0]) == 0:
                break


def uppmax(user, project_id, local_dir):
    """Sync files to UPPMAX project using rsync."""
    remote_dir = "{}@milou.uppmax.uu.se:/proj/{}/INBOX".format(user, project_id)
    sync_files(local_dir, remote_dir)
