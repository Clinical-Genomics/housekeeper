# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request

from housekeeper.server.ext import store

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')


@blueprint.route('/bundles')
def bundles():
    """Display bundles."""
    per_page = int(request.args.get('per_page', 30))
    page = int(request.args.get('page', 1))
    query = store.bundles()

    query_page = query.paginate(page, per_page=per_page)
    data = []
    for bundle_obj in query_page.items:
        bundle_data = bundle_obj.to_dict()
        bundle_data['versions'] = [version.to_dict() for version in bundle_obj.versions]
        data.append(bundle_data)

    return jsonify(bundles=data)
