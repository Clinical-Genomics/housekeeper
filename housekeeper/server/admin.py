# -*- coding: utf-8 -*-
from path import Path
import yaml


class UserAdmin(object):
    """docstring for UserAdmin"""
    def __init__(self, database_path=None):
        super(UserAdmin, self).__init__()
        self.database_path = Path(database_path) if database_path else None

    def init_app(self, app):
        """Initialize in Flask app context."""
        self.database_path = Path(app.config['USER_DATABASE_PATH'])

    def confirm(self, email):
        """Confirm that a user has been whitelisted."""
        # read in the file on every request
        with self.database_path.open('r') as in_handle:
            whitelisted_emails = yaml.load(in_handle)['whitelist']
        return email in whitelisted_emails
