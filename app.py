import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, Blueprint
from dotenv import load_dotenv
from db_utils.fetch_data import get_api_data
from app.config import create_context_processor


load_dotenv()
PASSWORD = os.getenv("APP_PASSWORD", "0000") 
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY', '51HgZrX9Q2bYlX3sYvPqL9aTgZrX9Q2b')
URL_PREFIX = os.getenv('URL_PREFIX', '').rstrip('/')

app = Flask(__name__, static_url_path=f"{URL_PREFIX}/static" if URL_PREFIX else None)
app.secret_key = APP_SECRET_KEY

# Initialize URL configuration context processor
url_config = create_context_processor(app)

# Create a blueprint for all routes with URL prefix
main_bp = Blueprint('main', __name__, url_prefix=URL_PREFIX if URL_PREFIX else None)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("main.index"))
        return render_template("password_incorrect.html")
    return render_template("password_form.html")

@main_bp.route('/logout')
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("main.login"))

@main_bp.route('/')
def index():
    """Route for the main page - serves the A/B Testing Dashboard."""
    if not session.get("logged_in"):
        return redirect(url_for("main.login"))
    
    # Get filter parameters from URL (for when filters are applied)
    test_name = request.args.get('test', 'Homepage Redesign')
    date_range = request.args.get('date_range', 'Last 7 days')
    metric_type = request.args.get('metric', 'Conversion Rate')

    template_data = get_api_data(test_name, date_range, metric_type)
    # URL configuration is now automatically injected via context processor
    return render_template('index.html', **template_data)


@main_bp.route('/dashboard')
def dashboard():
    """Alternative route for the dashboard (same as index)."""
    return index()


@main_bp.route("/api/data")
def api_data():
    """API endpoint to fetch A/B test data."""
    test_name = request.args.get('test', 'Homepage Redesign')
    date_range = request.args.get('date_range', 'Last 7 days')
    metric_type = request.args.get('metric', 'Conversion Rate')

    data = get_api_data(test_name, date_range, metric_type)
    return jsonify(data)

# Register the blueprint with the app
app.register_blueprint(main_bp)


def entry_point(request):
    return app


if __name__ == '__main__':
    # Get Flask configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8080))
    
    # Run the Flask app with configuration from .env
    app.run(debug=debug_mode, host=host, port=port)