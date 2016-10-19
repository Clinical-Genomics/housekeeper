# -*- coding: utf-8 -*-
import logging
import subprocess

log = logging.getLogger(__name__)


def launch(command):
    """ Launch a command

    Args:
        command (str): the bash command to launch

    Returns (str): stdout
    """

    try:
        command_line = command.split(' ')
        log.debug(' '.join(command_line))
        log.info(command_line)
        return subprocess.check_output(command_line)
    except subprocess.CalledProcessError as exception:
        exception.message = "Command '{}' failed.".format(' '.join(command_line))
        raise exception
