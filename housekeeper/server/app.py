# -*- coding: utf-8 -*-
"""Flask app module."""
import logging
import os

from flask import abort, Flask, render_template, request, redirect
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap
from flask_login import current_user, login_required
from werkzeug.contrib.fixers import ProxyFix

from housekeeper.store import Model, api
from housekeeper.store.models import User
from .admin import UserManagement


log = logging.getLogger(__name__)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# configuration
SECRET_KEY = os.environ.get('SECRET_KEY') or 'thisIsNotSecret!'
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
GOOGLE_OAUTH_CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
GOOGLE_OAUTH_CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
USER_DATABASE_PATH = os.environ['USER_DATABASE_PATH']
# serve boostrap assets locally is running in debug mode
BOOTSTRAP_SERVE_LOCAL = 'FLASK_DEBUG' in os.environ
if 'mysql' in SQLALCHEMY_DATABASE_URI:  # pragma: no cover
    SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False
TEMPLATES_AUTO_RELOAD = True
app.config.from_object(__name__)

# database setup
db = Alchy(Model=Model)
user = UserManagement(db, User)


@app.route('/')
def index():
    """Show dashboard."""
    if not current_user.is_authenticated:
        return render_template('index.html')

    to_analyzed = api.to_analyzed(db.session)
    return render_template('dashboard.html', to_analyzed=to_analyzed)


@app.route('/cases')
@login_required
def cases():
    """Overview all loaded cases."""
    page = int(request.args.get('page', '1'))
    qargs = {
        'query_str': request.args.get('query_str'),
        'per_page': 30,
        'status_to': request.args.get('status_to'),
    }
    cases_q = api.cases(query_str=qargs['query_str'],
                        status_to=qargs['status_to'])
    cases_page = cases_q.paginate(page, per_page=qargs['per_page'])
    return render_template('cases.html', cases=cases_page, qargs=qargs)


@app.route('/cases/<name>')
@login_required
def case(name):
    """Show more information about a case."""
    case_obj = api.case(name)
    if case_obj is None:
        return abort(404)
    return render_template('case.html', case=case_obj)


@app.route('/cases/<case_name>/postpone', methods=['POST'])
@login_required
def case_postpone(case_name):
    """Postpone clean up date for the latest run of a case."""
    run_obj = api.runs(case_name).first()
    if run_obj is None:
        return abort(404)
    api.postpone(run_obj)
    db.commit()
    return redirect(request.referrer)


@app.route('/samples')
@login_required
def samples():
    """Overview all loaded samples."""
    page = int(request.args.get('page', '1'))
    status_to = request.args.get('status_to')
    qargs = {
        'query_str': request.args.get('query_str'),
        'per_page': 30,
        'status_to': status_to
    }
    samples_q = api.samples(query_str=qargs['query_str'], status_to=status_to)
    samples_page = samples_q.paginate(page, per_page=qargs['per_page'])
    return render_template('samples.html', samples=samples_page, qargs=qargs)


# hookup extensions to app
Bootstrap(app)
db.init_app(app)
user.init_app(app)
