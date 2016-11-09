# -*- coding: utf-8 -*-
"""Flask app module."""
import logging
import os

from flask import (abort, Flask, render_template, request, redirect, url_for,
                   jsonify, session, flash)
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_login import (current_user, LoginManager, login_user, logout_user,
                         login_required)

from housekeeper.store import Model, api
from housekeeper.store.models import User, OAuth
from .admin import UserAdmin


log = logging.getLogger(__name__)

app = Flask(__name__)

# configuration
SECRET_KEY = os.environ.get('SECRET_KEY') or 'thisIsNotSecret!'
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
USER_DATABASE_PATH = os.environ['USER_DATABASE_PATH']
if 'mysql' in SQLALCHEMY_DATABASE_URI:  # pragma: no cover
    SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False
TEMPLATES_AUTO_RELOAD = True
app.config.from_object(__name__)

# authentication
login_bp = make_google_blueprint(client_id=os.environ['GOOGLE_ID'],
                                 client_secret=os.environ['GOOGLE_SECRET'],
                                 scope=['profile', 'email'])
app.register_blueprint(login_bp, url_prefix='/login')

# database setup
db = Alchy(Model=Model)
user_admin = UserAdmin()

# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'google.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# setup SQLAlchemy login backend
login_bp.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)


@oauth_authorized.connect_via(login_bp)
def google_loggedin(login_bp, token):
    """Create/login local user on successful OAuth login."""
    if not token:
        flash("Failed to log in with {}".format(login_bp.name), 'danger')
        return redirect(url_for('index'))

    # figure out who the user is
    resp = login_bp.session.get('/oauth2/v1/userinfo?alt=json')

    if resp.ok:
        userinfo = resp.json()

        # check if the user is whitelisted
        email = userinfo['email']
        if not user_admin.confirm(email):
            flash("email not whitelisted: {}".format(email), 'danger')
            return redirect(url_for('index'))

        user = User.query.filter_by(google_id=userinfo['id']).first()
        if user:
            user.name = userinfo['name']
            user.avatar = userinfo['picture']
        else:
            user = User(google_id=userinfo['id'], name=userinfo['name'],
                        avatar=userinfo['picture'])
            db.add(user)

        db.commit()
        login_user(user)
        flash('Successfully signed in with Google', 'success')
    else:
        message = "Failed to fetch user info from {}".format(login_bp.name)
        flash(message, 'danger')

    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out', 'info')
    return redirect(url_for('index'))


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
    }
    cases_q = api.cases(query_str=qargs['query_str'])
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
    qargs = {
        'query_str': request.args.get('query_str'),
        'per_page': 30,
    }
    samples_q = api.samples(query_str=qargs['query_str'])
    samples_page = samples_q.paginate(page, per_page=qargs['per_page'])
    return render_template('samples.html', samples=samples_page, qargs=qargs)


# hookup extensions to app
Bootstrap(app)
db.init_app(app)
login_manager.init_app(app)
user_admin.init_app(app)
