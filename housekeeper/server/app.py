# -*- coding: utf-8 -*-
"""Flask app module."""
import logging
import os

from flask import abort, Flask, render_template, request, redirect, url_for
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap

from housekeeper.store import Model, api

log = logging.getLogger(__name__)

app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'thisIsNotSecret!'
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
if 'mysql' in SQLALCHEMY_DATABASE_URI:  # pragma: no cover
    SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False
TEMPLATES_AUTO_RELOAD = True
app.config.from_object(__name__)

Bootstrap(app)
db = Alchy(app, Model=Model)


@app.route('/')
def index():
    """Just redirect for now."""
    return redirect(url_for('cases'))


@app.route('/cases')
def cases():
    """Overview all loaded cases."""
    cases_q = api.cases().limit(20)
    return render_template('cases.html', cases=cases_q)


@app.route('/cases/<case_name>/postpone', methods=['POST'])
def case_postpone(case_name):
    """Postpone case archival date."""
    case_obj = api.case(case_name)
    if case_obj is None:
        return abort(404)
    api.postpone(case_obj.analysis)
    db.commit()
    return redirect(request.referrer)
