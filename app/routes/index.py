import os
from flask import Blueprint, render_template, session, redirect, request, url_for

from db_utils.fetch_data import get_api_data

bp = Blueprint('index', __name__)

API_BASE_URL = os.getenv('API_BASE_URL', '/api/data')

@bp.route("/")
def index():
    """Route for the main page - serves the A/B Testing Dashboard."""
    if not session.get("logged_in"):
        return redirect(url_for("main.login.login"))
    
    # Get filter parameters from URL (for when filters are applied)
    test_name = request.args.get('test', 'Homepage Redesign')
    date_range = request.args.get('date_range', 'Last 7 days')
    metric_type = request.args.get('metric', 'Conversion Rate')

    template_data = get_api_data(test_name, date_range, metric_type)
    template_data['api_base_url'] = API_BASE_URL
    return render_template('index.html', **template_data)