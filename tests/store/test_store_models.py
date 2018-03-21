# -*- coding: utf-8 -*-
from pathlib import Path
import datetime

from housekeeper.store import models


def test_Version():
    # GIVEN a bundle version
    bundle_obj = models.Bundle(name='handsomepig')
    now = datetime.datetime.now()
    version_obj = models.Version(created_at=now, bundle=bundle_obj, app_root='')
    # WHEN accessing the relative root path
    root_dir = version_obj.root_dir
    # THEN it should point to the correct folder
    now_str = str(now.date())
    assert root_dir == Path('handsomepig') / now_str
