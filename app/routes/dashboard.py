import os
from flask import Blueprint, redirect, url_for, session

from app.routes import index

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
def dashboard():
    """Alternative route for the dashboard (same as index)."""
    if not session.get("logged_in"):
        return redirect(url_for("main.login.login"))
    return index.index()