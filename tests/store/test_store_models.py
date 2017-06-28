# -*- coding: utf-8 -*-
from pathlib import Path
import datetime

from housekeeper.store import models


def test_User():
    # GIVEN a user
    user_obj = models.User(name='Quentin Tarantino', email='quentin@pulpfiction.com')
    # WHEN accessing the first name
    first_name = user_obj.first_name
    # THEN it should be correct
    assert first_name == 'Quentin'


def test_Version():
    # GIVEN a bundle version
    bundle_obj = models.Bundle(name='handsomepig')
    now = datetime.datetime.now()
    version_obj = models.Version(created_at=now, bundle=bundle_obj)
    # WHEN accessing the relative root path
    root_dir = version_obj.root_dir
    # THEN it should point to the correct folder
    now_str = str(now.date())
    assert root_dir == Path('handsomepig') / now_str
