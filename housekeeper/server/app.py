# -*- coding: utf-8 -*-
"""Flask app module."""
from __future__ import division
import logging
import os

from dateutil.parser import parse as parse_date
from flask import abort, Flask, render_template, request, redirect
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap
from flask_login import current_user, login_required
from werkzeug.contrib.fixers import ProxyFix

from housekeeper.constants import EXTRA_STATUSES
from housekeeper.store import Model, api, Sample, Case, AnalysisRun
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

app.jinja_env.globals['EXTRA_STATUSES'] = EXTRA_STATUSES


@app.route('/')
def index():
    """Show dashboard."""
    if not current_user.is_authenticated:
        return render_template('index.html')

    plots = []
    for category in ['wgs', 'wes', 'tga']:
        all_samples = Sample.query.filter_by(category=category)
        samples_count = all_samples.count()
        sequenced_count = all_samples.filter(Sample.sequenced_at != None).count()
        plots.append({
            'category': category,
            'total': samples_count,
            'sequenced': sequenced_count,
            'sequenced_percent': (sequenced_count / samples_count) * 100,
            'to_sequenced': api.to_sequenced(db.session, category),
            'to_analyzed': api.to_analyzed(db.session, category),
        })

    all_cases = Case.query
    cases_count = all_cases.count()
    analyzed_cases = (all_cases.join(Case.runs)
                               .filter(AnalysisRun.analyzed_at != None)
                               .count())
    data = {
        'cases': cases_count,
        'analyzed_percent': (analyzed_cases / cases_count) * 100,
        'plots': plots,
    }
    return render_template('dashboard.html', **data)


@app.route('/cases')
@login_required
def cases():
    """Overview all loaded cases."""
    missing_category = request.args.get('missing')
    if missing_category == 'empty':
        missing_category = None
    page = int(request.args.get('page', '1'))
    qargs = {
        'query_str': request.args.get('query_str'),
        'per_page': 30,
        'missing': missing_category,
    }
    version = 'v4' if qargs['missing'] == 'delivered' else None
    cases_q = api.cases(query_str=qargs['query_str'], missing=qargs['missing'],
                        version=version)
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


@app.route('/cases/<case_name>/onhold', methods=['POST'])
@login_required
def case_onhold(case_name):
    """Toggle onhold status for a case."""
    case_obj = api.case(case_name)
    if case_obj is None:
        return abort(404)
    case_obj.is_onhold = False if case_obj.is_onhold else True
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


@app.route('/comments/<int:case_id>', methods=['POST'])
@login_required
def comments(case_id):
    """Interact with comments."""
    case_obj = Case.query.get(case_id)
    if case_obj is None:
        return abort(404)
    new_comment = request.form['comment']
    case_obj.comment = new_comment
    db.commit()
    return redirect(request.referrer)


@app.route('/queue')
@login_required
def queue():
    """Overview of status of samples/cases."""
    data = dict(
        samples_to_receive=api.samples(status_to='receive'),
        samples_to_sequence=api.samples(status_to='sequence'),
        cases_to_analyze=api.cases(missing='analyzed', onhold=False),
        cases_to_deliver=api.cases(missing='delivered'),
    )
    return render_template('queue.html', **data)


@app.route('/cases/<int:case_id>/manual', methods=['POST'])
@login_required
def case_manual(case_id):
    """Mark a case as manual."""
    case_obj = Case.query.get(case_id)
    if case_obj is None:
        return abort(404)
    case_obj.is_manual = True
    db.commit()
    return redirect(request.referrer)


@app.route('/samples/<int:sample_id>/sequenced', methods=['POST'])
@login_required
def sample_sequenced(sample_id):
    """Mark a sample as sequenced."""
    sample_obj = Sample.query.get(sample_id)
    if sample_obj is None:
        return abort(404)
    sequence_date = parse_date(request.form['when'])
    sample_obj.sequenced_at = sequence_date
    db.commit()
    return redirect(request.referrer)


# hookup extensions to app
Bootstrap(app)
db.init_app(app)
user.init_app(app)
