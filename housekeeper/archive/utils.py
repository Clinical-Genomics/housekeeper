# -*- coding: utf-8 -*-
from datetime import date as make_date
from subprocess import CalledProcessError
import logging

from housekeeper.store import api
from housekeeper.compile.utils import launch

log = logging.getLogger(__name__)


def on_pdc(file_path, date=None):
    """Check if a file is on PDC """

    try:
        log.debug('dsmc q archive {}'.format(file_path))
        launch('dsmc q archive {}'.format(file_path), envs={'DSM_DIR':'/opt/adsm_clinical'})
    except CalledProcessError as dsmc_exc:
        if dsmc_exc.returncode == 8:
            return False
        raise dsmc_exc
    return True


def send_to_pdc(file_path):
    """ Send a file to PDC"""
    log.info('sending: {}'.format(file_path))
    log.debug('dsmc archive {}'.format(file_path))
    launch('dsmc archive {}'.format(file_path), envs={'DSM_DIR':'/opt/adsm_clinical'})
