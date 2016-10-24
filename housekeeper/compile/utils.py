# -*- coding: utf-8 -*-
import logging
import subprocess
import os

log = logging.getLogger(__name__)



def launch(command, envs=None):
    """ Launch a command

    Args:
        command (str): the bash command to launch

    Returns (str): stdout
    """

    if envs:
        os.environ.update(envs)

    try:
        command_line = command.split(' ')
        log.debug(' '.join(command_line))
        log.info(command_line)
        return subprocess.check_output(command_line)
    except subprocess.CalledProcessError as exception:
        exception.message = "Command '{}' failed.".format(' '.join(command_line))
        raise exception
